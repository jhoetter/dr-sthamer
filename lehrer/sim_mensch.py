"""Probelauf-Werkzeug: führt die Cockpit-Aktionen des Menschen aus (wie Klicks im Browser).

Nur für Probeläufe und Tests der Lehrenden. Teilnehmende und Claude nutzen es nie: Senden, Freigeben,
Ablehnen, Uhr vorspulen und Postfach abrufen sind absichtlich nur im Cockpit möglich.

  python scripts/sim_mensch.py [--port 3005] welle 2 hydrant
  python scripts/sim_mensch.py senden 3 | freigeben 3 | ablehnen 3 "Frist falsch" | stoppen 3 | uhr 24
  python scripts/sim_mensch.py speichern 3 --text "Neuer Text"   (ändert Text, Betreff, Empfänger wie im Cockpit)
  python scripts/sim_mensch.py fall MSG-1-02 | status | entwuerfe | postausgang | protokoll | bericht
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def holen(port, pfad, token=None, body=None):
    url = "http://127.0.0.1:%d%s" % (port, pfad)
    if body is None:
        req = Request(url)
    else:
        req = Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                      headers={"Content-Type": "application/json", "X-Sthamer-Token": token or ""})
    try:
        with urlopen(req, timeout=20) as r:
            return r.status, r.read().decode("utf-8")
    except HTTPError as e:
        return e.code, e.read().decode("utf-8")


def main():
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding="utf-8")
        except Exception:
            pass
    p = argparse.ArgumentParser()
    p.add_argument("--port", type=int, default=3005)
    p.add_argument("aktion")
    p.add_argument("args", nargs="*")
    p.add_argument("--text")
    p.add_argument("--betreff")
    p.add_argument("--an")
    a = p.parse_args()
    _, html = holen(a.port, "/")
    m = re.search(r'name="sthamer-token" content="([^"]+)"', html)
    token = m.group(1) if m else ""
    lesen = {"status": "/api/status", "entwuerfe": "/api/entwuerfe", "postausgang": "/api/postausgang",
             "protokoll": "/api/protokoll", "bericht": "/api/bericht", "einschaetzungen": "/api/einschaetzungen",
             "faelle": "/api/faelle"}
    if a.aktion in lesen:
        code, text = holen(a.port, lesen[a.aktion])
    else:
        x = a.args
        wege = {
            "welle": ("/api/welle", lambda: {"welle": int(x[0]), "code": x[1] if len(x) > 1 else ""}),
            "fall": ("/api/fall", lambda: {"nachricht_id": x[0]}),
            "senden": ("/api/senden/" + (x[0] if x else ""), lambda: {}),
            "freigeben": ("/api/freigeben/" + (x[0] if x else ""), lambda: {}),
            "ablehnen": ("/api/ablehnen/" + (x[0] if x else ""), lambda: {"grund": x[1] if len(x) > 1 else ""}),
            "stoppen": ("/api/stoppen/" + (x[0] if x else ""), lambda: {}),
            "uhr": ("/api/uhr", lambda: {"stunden": float(x[0])}),
            "speichern": ("/api/entwurf/" + (x[0] if x else ""),
                          lambda: {k: v for k, v in (("text", a.text), ("betreff", a.betreff), ("an", a.an)) if v is not None}),
        }
        if a.aktion not in wege:
            print("Unbekannte Aktion. Siehe Kopf der Datei.", file=sys.stderr)
            return 2
        pfad, body = wege[a.aktion]
        code, text = holen(a.port, pfad, token, body())
    print("HTTP %d" % code)
    try:
        print(json.dumps(json.loads(text), ensure_ascii=False, indent=2))
    except ValueError:
        print(text[:500])
    return 0 if code < 400 else 1


if __name__ == "__main__":
    sys.exit(main())
