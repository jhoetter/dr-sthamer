"""Lehrer-Absicherung: Die Akzeptanzprüfungen finden auf dem Ausgangsstand die Lücken und bestehen mit den
Referenzlösungen, und mit der Referenz bleiben ALLE Prüfszenarien in tests/ grün.

Läuft nur bei den Lehrenden und in der CI: python -m unittest discover -s lehrer
Teilnehmende lassen nur tests/ laufen (nach ihrem korrekten Bau würde der Ausgangsstand-Teil sonst rot)."""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TESTS = ROOT / "lehrer"


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
            r = lauf(wurzel / "lehrer" / "referenz_anwenden.py", str(wurzel))
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            for n in (1, 2, 3, 4, 5):
                r = lauf(wurzel / "scripts" / "akzeptanz.py", str(n), "--root", str(wurzel))
                self.assertEqual(r.returncode, 0, "Drill %d mit Referenz:\n%s%s" % (n, r.stdout, r.stderr))
                self.assertNotIn("OPTIONAL ", r.stdout, "Drill %d: optionales Szenario offen:\n%s" % (n, r.stdout))
            r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests"], cwd=str(wurzel), capture_output=True,
                               timeout=600, encoding="utf-8", errors="replace")
            self.assertEqual(r.returncode, 0, "Mit der Referenz müssen alle Prüfszenarien in tests/ grün sein:\n" + r.stderr[-1500:])


if __name__ == "__main__":
    unittest.main()
