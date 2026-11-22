# -*- coding: utf-8 -*-
"""Reiter „Finanzen“: rechnet aus den Tabellen und schreibt dashboard-daten/finanzen.js.

Aufruf: python meine-ergebnisse/skripte/finanzen.py

Inhalt der Datei:
- zeilen: je Jahr (2025, 2026), Segment, Vertriebsweg, Schaumart die Summen Nettoumsatz (Konzernkurs des Jahres),
  Herstellkosten, Fracht (nach Litern verteilt), Positionen ohne Muster. Muster tragen Kosten, keinen Umsatz.
  Der Browser bildet Deckungsbeitrag und Marge immer aus diesen Summen (nie Margen mitteln).
- bruecke: Budget -> Ist 2026 (Deckungsbeitrag), gerechnet von bruecke.py (Ist zum Ist-Monatskurs, Budget zum Plankurs).
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import finanz_basis as fb
import gemeinsam as g
import bruecke as br

pos, kd, prod, pruef = fb.lade()
WEGE = ["direkt", "Händler", "Rahmenvertrag", "Notfallservice"]
segmente = sorted(set(k["segment"] for k in kd.values()))
schaumarten = sorted(set(p["schaumart"] for p in prod.values()))

acc = defaultdict(lambda: [0.0, 0.0, 0.0, 0, 0.0])
for p in pos:
    if p["jahr"] not in (2025, 2026):
        continue
    key = (p["jahr"], segmente.index(p["segment"]), WEGE.index(p["vw"]), schaumarten.index(p["schaumart"]))
    a = acc[key]
    a[0] += p["eur"]
    a[1] += p["hk"]
    a[2] += p["fracht"]
    if not p["muster"]:
        a[3] += 1
        a[4] += p["liter"]
zeilen = [[k[0], k[1], k[2], k[3], round(v[0], 4), round(v[1], 4), round(v[2], 4), v[3], round(v[4], 1)] for k, v in sorted(acc.items())]

r = br.rechne()
E = r["effekte"]
bruecke = {
    "budget_db": round(r["DBp"], 2), "budget_umsatz": round(r["Up"], 2), "budget_liter": r["Qp"],
    "ist_db": round(r["ist_db_gesamt"], 2), "ist_db_ohne_notfall": round(r["ist_db_zellen"], 2),
    "ist_umsatz_monat": round(r["ist_u_monat"], 2),
    "effekte": [
        {"name": "Mengeneffekt", "wert": round(E["menge"], 2), "bewertung": "(Ist-Liter − Plan-Liter) × Plan-DB je Liter im Durchschnitt"},
        {"name": "Mixeffekt", "wert": round(E["mix"], 2), "bewertung": "Ist-Liter je Zelle × Plan-DB je Liter der Zelle, minus Ist-Liter × Plan-Durchschnitt"},
        {"name": "Preiseffekt", "wert": round(E["preis"], 2), "bewertung": "Ist-Umsatz zum Plankurs minus Ist-Liter × Plan-Preis je Liter der Zelle"},
        {"name": "Kosteneffekt", "wert": round(E["kosten"], 2), "bewertung": "Ist-Liter × Plan-Kosten je Liter minus Ist-Kosten (Herstellkosten und Fracht)"},
        {"name": "Fremdwährung", "wert": round(E["fx"], 2), "bewertung": "Ist-Betrag in Fremdwährung × (Ist-Monatskurs − Plankurs)"},
        {"name": "Notfallservice", "wert": round(E["notfall"], 2), "bewertung": "ganzer Deckungsbeitrag der Notfalllieferung, nicht budgetiert"},
    ],
    "summe_effekte": round(r["summe"], 2), "gesamtabweichung": round(r["gesamtabw"], 2),
    "differenz": round(r["summe"] - r["gesamtabw"], 6),
    "notfall": {"liter": r["notfall"]["l"], "umsatz_monat": round(r["notfall"]["u_monat"], 2), "hk": round(r["notfall"]["hk"], 2),
                "fracht": round(r["notfall"]["fracht"], 2), "db": round(r["nf_db"], 2)},
    "kurse_2026": g.kurse()["2026"],
}
daten = {
    "segmente": segmente, "wege": WEGE, "schaumarten": schaumarten, "zeilen": zeilen, "bruecke": bruecke,
    "min_positionen": 20,
}
ziel = os.path.join(g.BASIS, "meine-ergebnisse", "dashboard-daten")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "finanzen.js"), "w", encoding="utf-8") as f:
    f.write("/* erzeugt von skripte/finanzen.py, nicht von Hand ändern */\n")
    f.write("const FINANZEN_DATEN = " + json.dumps(daten, ensure_ascii=False, separators=(",", ":")) + ";\n")

# ---- Kontrollzahlen (stehen im Chat) ----
print("Zeilen in finanzen.js:", len(zeilen))
for jahr in (2025, 2026):
    u = sum(z[4] for z in zeilen if z[0] == jahr)
    hk = sum(z[5] for z in zeilen if z[0] == jahr)
    fr = sum(z[6] for z in zeilen if z[0] == jahr)
    print(jahr, "Umsatz", g.de(u, 2), "HK", g.de(hk, 2), "Fracht", g.de(fr, 2), "DB", g.de(u - hk - fr, 2), "Marge {:.2f} %".format((u - hk - fr) / u * 100))
print("Brücke: Summe der Effekte", g.de(r["summe"], 2), "Gesamtabweichung", g.de(r["gesamtabw"], 2), "Differenz", round(r["summe"] - r["gesamtabw"], 6))
