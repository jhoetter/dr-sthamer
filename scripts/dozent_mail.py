"""Mails aus dem Dozenten-Postfach senden und lesen (nur für Lehrende, aus der eigenen Claude-Sitzung am Dozententisch).

Der Schlüssel des Dozenten-Postfachs steht nur in der lokalen `.env` (nie im Repository):
    DOZENT_AGENTMAIL_API_KEY=am_...
    DOZENT_AGENTMAIL_INBOX_ID=name@agentmail.to

    python3 scripts/dozent_mail.py senden --betreff "Willkommen" --text "Hallo zusammen ..."   # an sthamer@agentmail.to
    python3 scripts/dozent_mail.py senden --an name@firma.de --betreff ... --text ...
    python3 scripts/dozent_mail.py lesen                                                     # neueste empfangene Mails
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from sthamer_sys import agentmail  # noqa: E402

STANDARD_AN = "sthamer@agentmail.to"


def env_lesen() -> dict:
    werte = {}
    pfad = ROOT / ".env"
    if pfad.is_file():
        for zeile in pfad.read_text(encoding="utf-8").splitlines():
            zeile = zeile.strip()
            if zeile and not zeile.startswith("#") and "=" in zeile:
                k, v = zeile.split("=", 1)
                werte[k.strip()] = v.strip().strip('"').strip("'")
    return werte


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="befehl", required=True)
    s = sub.add_parser("senden")
    s.add_argument("--an", default=STANDARD_AN)
    s.add_argument("--betreff", required=True)
    s.add_argument("--text", required=True)
    sub.add_parser("lesen")
    a = p.parse_args()
    e = env_lesen()
    schluessel, postfach = e.get("DOZENT_AGENTMAIL_API_KEY", ""), e.get("DOZENT_AGENTMAIL_INBOX_ID", "")
    if not schluessel or not postfach:
        print("In .env fehlen DOZENT_AGENTMAIL_API_KEY und DOZENT_AGENTMAIL_INBOX_ID.", file=sys.stderr)
        return 1
    try:
        if a.befehl == "senden":
            agentmail.senden(schluessel, postfach, a.an, a.betreff, a.text)
            print("Gesendet von %s an %s: %s" % (postfach, a.an, a.betreff))
        else:
            alle = [m for m in agentmail.liste(schluessel, postfach, limit=20, seiten=1) if "received" in (m.get("labels") or [])]
            if not alle:
                print("Keine empfangenen Mails in %s." % postfach)
            for m in alle[:10]:
                voll = agentmail.nachricht(schluessel, postfach, m["message_id"])
                text = (voll.get("extracted_text") or voll.get("text") or "").strip().replace("\n", " ")[:160]
                print("%s | %s | %s\n    %s" % ((m.get("timestamp") or "")[:19], m.get("from"), m.get("subject"), text))
    except agentmail.MailFehler as err:
        print("Fehler: %s" % err, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
