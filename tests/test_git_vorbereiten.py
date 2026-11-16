"""Das Einrichten macht das Speichern des Stands auf einem frischen Gastprofil möglich (ZIP-Betrieb, keine Git-Identität)."""
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests.test_nachladen import kopie

GIT = shutil.which("git")


def git(wurzel, env, *args):
    return subprocess.run(["git"] + list(args), cwd=str(wurzel), env=env, capture_output=True, encoding="utf-8", errors="replace", timeout=60)


@unittest.skipUnless(GIT, "Git nicht installiert")
class GitVorbereitenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="Sthamer Git ")
        leer = Path(self.tmp.name) / "leere-git-konfiguration"
        leer.write_text("", encoding="utf-8")
        # frisches Gastprofil: weder globale noch systemweite Git-Konfiguration, damit keine Identität bekannt ist
        self.env = dict(os.environ, GIT_CONFIG_GLOBAL=str(leer), GIT_CONFIG_NOSYSTEM="1", STHAMER_NACHLADEN="0")
        for k in ("STHAMER_STATE_DIR", "STHAMER_OUTBOX_DIR", "STHAMER_DATA_DIR", "STHAMER_MENSCH"):
            self.env.pop(k, None)
        self.wurzel = kopie(Path(self.tmp.name) / "kopie")

    def tearDown(self):
        self.tmp.cleanup()

    def einrichten(self):
        r = subprocess.run([sys.executable, str(self.wurzel / "sthamer.py"), "setup"], cwd=str(self.wurzel), env=self.env,
                           capture_output=True, encoding="utf-8", errors="replace", timeout=120)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        return r.stdout

    def test_zip_betrieb_ohne_git_ordner_bekommt_einen_gespeicherten_ausgangsstand(self):
        self.assertFalse((self.wurzel / ".git").exists())
        out = self.einrichten()
        self.assertIn("Git-Ordner angelegt", out)
        log = git(self.wurzel, self.env, "log", "--oneline")
        self.assertEqual(len(log.stdout.strip().splitlines()), 1, log.stdout + log.stderr)
        self.assertTrue(git(self.wurzel, self.env, "config", "--local", "user.email").stdout.strip())
        tracked = git(self.wurzel, self.env, "ls-files").stdout
        for privat in (".mcp.json", ".data/", "postausgang/"):
            self.assertNotIn(privat, tracked)
        # und danach lässt sich der Stand speichern, wie es Claude im Drill tut
        (self.wurzel / "meine-aenderung.txt").write_text("x", encoding="utf-8")
        self.assertEqual(git(self.wurzel, self.env, "add", "meine-aenderung.txt").returncode, 0)
        r = git(self.wurzel, self.env, "commit", "-q", "-m", "Mein Stand")
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

    def test_vorhandener_klon_ohne_identitaet_bekommt_sie_lokal_und_bleibt_sonst_unberuehrt(self):
        git(self.wurzel, self.env, "init", "-q")
        git(self.wurzel, self.env, "add", "-A")
        self.assertEqual(git(self.wurzel, self.env, "-c", "user.name=a", "-c", "user.email=a@b.invalid", "commit", "-q", "-m", "x").returncode, 0)
        out = self.einrichten()
        self.assertNotIn("Git-Ordner angelegt", out)
        self.assertEqual(git(self.wurzel, self.env, "log", "--oneline").stdout.strip().count("\n"), 0)  # keine zusätzlichen Commits
        self.assertTrue(git(self.wurzel, self.env, "config", "--local", "user.name").stdout.strip())

    def test_vorhandene_identitaet_wird_nicht_ueberschrieben(self):
        git(self.wurzel, self.env, "init", "-q")
        git(self.wurzel, self.env, "config", "--local", "user.name", "Erika Muster")
        git(self.wurzel, self.env, "config", "--local", "user.email", "erika@beispiel.invalid")
        self.einrichten()
        self.assertEqual(git(self.wurzel, self.env, "config", "--local", "user.name").stdout.strip(), "Erika Muster")


if __name__ == "__main__":
    unittest.main()
