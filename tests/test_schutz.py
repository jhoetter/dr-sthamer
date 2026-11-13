"""Menschen-Aktionen laufen nur im Cockpit-Prozess, nicht in einem Skript, das Claude startet."""
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.request import Request, urlopen

from tests.test_nachladen import kopie

SKRIPT = '''
import json
from sthamer_sys import domain
domain.welle_freischalten(1, akteur="system")
fid = domain.fall_anlegen("MSG-1-02", akteur="claude")["fall_id"]
eid = domain.entwurf_anlegen(fid, "a.lindemann@ff-bergheim-land.example.com", "A", "Guten Tag", [], "claude")["entwurf_id"]
ergebnis = {}
for name, fn in [("senden", lambda: domain.senden(eid)), ("freigeben", lambda: domain.freigeben(eid)),
                 ("ablehnen", lambda: domain.ablehnen(eid, "x")), ("uhr", lambda: domain.uhr_vorspulen(1)),
                 ("runde2", lambda: domain.welle_freischalten(2, "hydrant")), ("faellige", lambda: domain.faellige_senden())]:
    try:
        fn(); ergebnis[name] = "ERLAUBT"
    except domain.FachFehler as e:
        ergebnis[name] = "gesperrt: " + str(e)[:40]
    except Exception as e:
        ergebnis[name] = "anderer Fehler: %r" % e
domain.notiz(fid, "Claude darf notieren", "claude")
ergebnis["stoppen"] = "fehlerfrei" if True else ""
print(json.dumps(ergebnis))
'''


class SchutzTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="Sthamer Schutz ")
        self.wurzel = kopie(Path(self.tmp.name) / "kopie")
        self.env = {k: v for k, v in os.environ.items() if k not in ("STHAMER_MENSCH", "STHAMER_DATA_DIR")}
        self.env.update(STHAMER_NACHLADEN="0", STHAMER_STATE_DIR=str(self.wurzel / ".data"), STHAMER_OUTBOX_DIR=str(self.wurzel / "postausgang"))

    def tearDown(self):
        self.tmp.cleanup()

    def test_in_einem_skript_sind_menschen_aktionen_gesperrt(self):
        r = subprocess.run([sys.executable, "-c", SKRIPT], cwd=str(self.wurzel), env=self.env, capture_output=True, timeout=60,
                           encoding="utf-8", errors="replace")
        self.assertEqual(r.returncode, 0, r.stderr)
        erg = json.loads(r.stdout.strip().splitlines()[-1])
        for name in ("senden", "freigeben", "ablehnen", "uhr", "runde2", "faellige"):
            self.assertTrue(erg[name].startswith("gesperrt"), "%s: %s" % (name, erg[name]))
        self.assertFalse((self.wurzel / "postausgang").exists() and any((self.wurzel / "postausgang").iterdir()), "nichts gesendet")

    def test_das_cockpit_schaltet_sich_selbst_frei(self):
        proc = subprocess.Popen([sys.executable, str(self.wurzel / "sthamer.py"), "serve", "--port", "3098"], env=self.env,
                                cwd=str(self.wurzel), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(60):
                try:
                    with urlopen("http://127.0.0.1:3098/", timeout=3) as r:
                        html = r.read().decode("utf-8")
                    break
                except Exception:
                    time.sleep(0.25)
            else:
                self.fail("Cockpit startet nicht")
            token = html.split('name="sthamer-token" content="')[1].split('"')[0]
            req = Request("http://127.0.0.1:3098/api/welle", data=json.dumps({"welle": 2, "code": "hydrant"}).encode("utf-8"),
                          method="POST", headers={"Content-Type": "application/json", "X-Sthamer-Token": token})
            with urlopen(req, timeout=10) as r:
                self.assertEqual(r.status, 200)
        finally:
            proc.terminate()
            proc.wait(timeout=20)


if __name__ == "__main__":
    unittest.main()
