"""Verschlüsselt den Postfach-Schlüssel für das öffentliche Repository (nur für Lehrende, einmal vor dem Workshop).

Aufruf (Mac/Linux), Schlüssel und Passwort nur über die Umgebung, nie als Dateiinhalt oder Parameter:

    AGENTMAIL_API_KEY=am_... AGENTMAIL_INBOX_ID=name@agentmail.to POSTFACH_PASSWORT=kern-lila-tisch-42 python3 scripts/postfach_verschluesseln.py

Schreibt `data/agentmail.enc` (nur diese verschlüsselte Datei kommt ins Repository). Das Passwort sagst du erst am Workshop-Tag
an; die Teilnehmenden geben es im Cockpit unter „E-Mail“ ein. Nach dem Workshop den Schlüssel bei AgentMail löschen.
Tipp für das Passwort: drei zufällige Wörter und eine Zahl; nichts, was man aus dem Namen des Repos erraten kann.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sthamer_sys import agentmail  # noqa: E402
from sthamer_sys.paths import data_dir  # noqa: E402


def main() -> int:
    schluessel = os.environ.get("AGENTMAIL_API_KEY", "").strip()
    postfach = os.environ.get("AGENTMAIL_INBOX_ID", "").strip()
    passwort = os.environ.get("POSTFACH_PASSWORT", "").strip()
    if not schluessel.startswith("am_") or "@" not in postfach or not passwort:
        print("Es fehlen AGENTMAIL_API_KEY (beginnt mit am_), AGENTMAIL_INBOX_ID (Adresse) oder POSTFACH_PASSWORT.", file=sys.stderr)
        return 1
    try:
        agentmail.pruefen(schluessel, postfach)
        blob = agentmail.verschluesseln(schluessel, passwort, postfach)
        assert agentmail.entschluesseln(blob, passwort) == schluessel
    except agentmail.MailFehler as e:
        print("Abgebrochen: %s" % e, file=sys.stderr)
        return 1
    ziel = data_dir() / "agentmail.enc"
    with open(str(ziel), "w", encoding="utf-8", newline="\n") as f:
        json.dump(blob, f, indent=2)
        f.write("\n")
    print("Fertig: %s (Postfach %s). Der Schlüssel selbst steht nirgends im Klartext." % (ziel, postfach))
    return 0


if __name__ == "__main__":
    sys.exit(main())
