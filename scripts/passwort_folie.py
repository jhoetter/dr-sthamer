"""Schreibt das Postfach-Passwort aus der lokalen `.env` in `tag2/impuls/passwort.js`, damit die Passwort-Folie im Vortrag es zeigen kann.

Beide Dateien sind von Git ausgeschlossen (.gitignore) und kommen nie ins Repository. Aufruf: python3 scripts/passwort_folie.py
`.env` im Hauptordner enthält eine Zeile:  POSTFACH_PASSWORT=drei-zufaellige-woerter-42
Fehlt die Datei passwort.js, steht auf der Folie „steht an der Tafel“.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def env_lesen(pfad: Path) -> dict:
    werte = {}
    if pfad.is_file():
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if not zeile or zeile.startswith("#") or "=" not in zeile:
                continue
            k, v = zeile.split("=", 1)
            werte[k.strip()] = v.strip().strip('"').strip("'")
    return werte


def main() -> int:
    pw = env_lesen(ROOT / ".env").get("POSTFACH_PASSWORT", "")
    if not pw:
        print("In .env fehlt die Zeile POSTFACH_PASSWORT=…", file=sys.stderr)
        return 1
    ziel = ROOT / "tag2" / "impuls" / "passwort.js"
    with open(str(ziel), "w", encoding="utf-8", newline="\n") as f:
        f.write("window.POSTFACH_PASSWORT = %s;\n" % json.dumps(pw, ensure_ascii=False))
    print("Fertig: %s (nicht im Repository)." % ziel)
    return 0


if __name__ == "__main__":
    sys.exit(main())
