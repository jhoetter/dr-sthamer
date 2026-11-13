"""Änderungen am Programm gelten sofort: im Werkzeug-Server von Claude und im Cockpit, ohne Neustart."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent


def kopie(ziel: Path) -> Path:
    ignor = shutil.ignore_patterns(".git", ".data", "postausgang", "__pycache__", "dozent", ".mcp.json", "bericht.md")
    shutil.copytree(str(ROOT), str(ziel), ignore=ignor)
    return ziel


def anfassen(datei: Path, zusatz: str) -> None:
    """Datei ändern und die Änderungszeit sicher nach vorn setzen (manche Systeme messen grob)."""
    with open(str(datei), "a", encoding="utf-8", newline="\n") as f:
        f.write(zusatz)
    t = time.time() + 5
    os.utime(str(datei), (t, t))


class Mcp:
    def __init__(self, wurzel: Path, env):
        self.p = subprocess.Popen([sys.executable, str(wurzel / "sthamer.py"), "mcp"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, env=env, cwd=str(wurzel))
        self.n = 0

    def rufe(self, methode, params=None):
        self.n += 1
        self.p.stdin.write((json.dumps({"jsonrpc": "2.0", "id": self.n, "method": methode, "params": params or {}}) + "\n").encode("utf-8"))
        self.p.stdin.flush()
        return json.loads(self.p.stdout.readline().decode("utf-8"))["result"]

    def werkzeug(self, name, args):
        r = self.rufe("tools/call", {"name": name, "arguments": args})
        return r.get("isError", False), r["content"][0]["text"]

    def ende(self):
        self.p.stdin.close()
        self.p.wait(timeout=20)
        self.p.stdout.close()
        self.p.stderr.close()


class NachladenTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="Sthamer Nachladen ")
        self.wurzel = kopie(Path(self.tmp.name) / "kopie")
        self.env = dict(os.environ, STHAMER_NACHLADEN="1", STHAMER_STATE_DIR=str(self.wurzel / ".data"),
                        STHAMER_OUTBOX_DIR=str(self.wurzel / "postausgang"), STHAMER_DATA_DIR=str(self.wurzel / "data"))
        self.env.pop("STHAMER_DATA_DIR")  # Standard: data/ der Kopie

    def tearDown(self):
        self.tmp.cleanup()

    def test_werkzeug_server_laedt_geaenderte_pruefung_ohne_neustart(self):
        m = Mcp(self.wurzel, self.env)
        try:
            datei = self.wurzel / "sthamer_sys" / "belegpruefung.py"
            original = datei.read_text(encoding="utf-8")
            m.rufe("initialize", {"protocolVersion": "2025-06-18"})
            fehler, text = m.werkzeug("create_case", {"nachricht_id": "MSG-1-02"})
            self.assertFalse(fehler, text)
            fid = json.loads(text)["fall_id"]
            args = {"fall_id": fid, "an": "a.lindemann@ff-bergheim-land.example.com", "betreff": "A", "text": "Guten Tag", "belege": []}
            fehler, text = m.werkzeug("create_draft", args)
            self.assertFalse(fehler, text)  # Ausgangsstand: keine Prüfung
            anfassen(self.wurzel / "sthamer_sys" / "belegpruefung.py",
                     "\n\ndef pruefe_entwurf(an, betreff, text, belege):\n    return ['Geändert: Beleg fehlt.'] if not belege else []\n")
            fehler, text = m.werkzeug("create_draft", args)
            self.assertTrue(fehler, "Die geänderte Prüfung muss sofort gelten")
            self.assertIn("Geändert: Beleg fehlt", text)
            anfassen(self.wurzel / "sthamer_sys" / "belegpruefung.py", "\n\ndef pruefe_entwurf(an, betreff, text, belege):\n    return ['Kaputt'\n")
            fehler, text = m.werkzeug("create_draft", dict(args, belege=[{"typ": "kunde", "ref": "K-1010"}]))
            self.assertFalse(fehler, "Bei Tippfehler bleibt der alte, funktionierende Code aktiv: " + text)
            fehler, status = m.werkzeug("get_workshop_status", {})
            self.assertIn("code_fehler", status)
            datei.write_text(original + "\n\ndef pruefe_entwurf(an, betreff, text, belege):\n    return ['Repariert: Beleg fehlt.'] if not belege else []\n", encoding="utf-8")
            t = time.time() + 10
            os.utime(str(datei), (t, t))
            fehler, text = m.werkzeug("create_draft", args)
            self.assertTrue(fehler, "Nach der Reparatur gilt wieder der neue Code: " + text)
            self.assertIn("Repariert", text)
            fehler, status = m.werkzeug("get_workshop_status", {})
            self.assertNotIn("code_fehler", status)
        finally:
            m.ende()

    def test_cockpit_laedt_nach_und_meldet_fehler_im_health(self):
        proc = subprocess.Popen([sys.executable, str(self.wurzel / "sthamer.py"), "serve", "--port", "3099"], env=self.env,
                                cwd=str(self.wurzel), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            def health():
                with urlopen("http://127.0.0.1:3099/api/health", timeout=5) as r:
                    return json.loads(r.read().decode("utf-8"))
            for _ in range(60):
                try:
                    h0 = health()
                    break
                except Exception:
                    time.sleep(0.25)
            else:
                self.fail("Cockpit startet nicht")
            self.assertIsNone(h0["code_fehler"])
            anfassen(self.wurzel / "sthamer_sys" / "domain.py", "\n\ndef kaputt(:\n")
            h1 = health()
            self.assertIsNotNone(h1["code_fehler"], "Tippfehler wird gemeldet")
            self.assertNotEqual(h1["code_geladen"], h0["code_geladen"])
            with urlopen("http://127.0.0.1:3099/api/status", timeout=5) as r:
                self.assertEqual(r.status, 200)  # der alte Code läuft weiter
            domain = self.wurzel / "sthamer_sys" / "domain.py"
            text = domain.read_text(encoding="utf-8").replace("\n\ndef kaputt(:\n", "\n")
            domain.write_text(text, encoding="utf-8")
            t = time.time() + 10
            os.utime(str(domain), (t, t))
            self.assertIsNone(health()["code_fehler"])
        finally:
            proc.terminate()
            proc.wait(timeout=20)


if __name__ == "__main__":
    unittest.main()
