"""Die Akzeptanzprüfungen müssen auf dem Ausgangsstand die Lücken finden und mit den Referenzlösungen bestehen."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def kopie(ziel: Path) -> Path:
    ignor = shutil.ignore_patterns(".git", ".data", "postausgang", "__pycache__", "dozent", ".mcp.json", "bericht.md")
    shutil.copytree(str(ROOT), str(ziel), ignore=ignor)
    return ziel


def lauf(skript, *args):
    return subprocess.run([sys.executable, str(skript)] + list(args), capture_output=True, timeout=300,
                          encoding="utf-8", errors="replace")


class ReferenzTest(unittest.TestCase):
    def test_ausgangsstand_hat_die_luecken_und_die_referenz_schliesst_sie(self):
        with tempfile.TemporaryDirectory(prefix="Sthamer Referenz ") as t:
            wurzel = kopie(Path(t) / "kopie")
            for n in (1, 2, 3, 4):
                r = lauf(wurzel / "scripts" / "akzeptanz.py", str(n), "--root", str(wurzel))
                self.assertEqual(r.returncode, 1, "Drill %d sollte auf dem Ausgangsstand NICHT bestehen:\n%s" % (n, r.stdout))
            r = lauf(wurzel / "scripts" / "referenz_anwenden.py", str(wurzel))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for n in (1, 2, 3, 4, 5):
                r = lauf(wurzel / "scripts" / "akzeptanz.py", str(n), "--root", str(wurzel))
                self.assertEqual(r.returncode, 0, "Drill %d mit Referenz:\n%s%s" % (n, r.stdout, r.stderr))
                self.assertNotIn("OPTIONAL ", r.stdout, "Drill %d: optionales Szenario offen:\n%s" % (n, r.stdout))


if __name__ == "__main__":
    unittest.main()
