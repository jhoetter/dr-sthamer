# -*- coding: utf-8 -*-
"""Reiter „Wachstum“: rechnet aus den Tabellen und schreibt dashboard-daten/wachstum.js.

Aufruf: python meine-ergebnisse/skripte/wachstum.py

Der Browser rechnet bei jedem Filter neu aus den hier geschriebenen Zeilen (Summen und Zähler,
Quoten nie gemittelt). Die Kontrollzahlen am Ende des Laufs stehen im Chat.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g

pos, stat = g.positionen()
kd = g.kunden()

ARTEN = ["Nachfüllung", "Erstbefüllung", "Notfall"]
WEGE = ["direkt", "Händler", "Rahmenvertrag", "Notfallservice"]
kunden_ids = sorted(kd)
kidx = {k: i for i, k in enumerate(kunden_ids)}

zeilen = defaultdict(lambda: [0.0, 0.0, 0])
for p in pos:
    if p["muster"]:
        continue
    key = (p["jahr"], kidx[p["kunde"]], WEGE.index(p["vw"]), ARTEN.index(p["art_auftrag"]))
    z = zeilen[key]
    z[0] += p["liter"]
    z[1] += p["eur"]
    z[2] += 1
zeilen_liste = [[k[0], k[1], k[2], k[3], round(v[0], 1), round(v[1], 4), v[2]] for k, v in sorted(zeilen.items())]

notfall = []
for p in sorted(pos, key=lambda p: p["ld"]):
    if p["art_auftrag"] == "Notfall" and p["art"] == "Lieferung":
        notfall.append({"datum": p["ld"].strftime("%d.%m.%Y"), "jahr": p["jahr"], "kunde": kd[p["kunde"]]["name"],
                        "segment": kd[p["kunde"]]["segment"], "land": kd[p["kunde"]]["land"], "liter": p["liter"], "eur": round(p["eur"], 2)})

daten = {
    "jahre": [2021, 2022, 2023, 2024, 2025, 2026],
    "teiljahr": 2027,
    "arten": ARTEN,
    "wege": WEGE,
    "kunden": [{"id": k, "segment": kd[k]["segment"], "land": kd[k]["land"]} for k in kunden_ids],
    "zeilen": zeilen_liste,
    "notfall": notfall,
    "ampel": {"wachstum": 0.05, "rueckgang": -0.05, "min_positionen": 20},
}

ziel = os.path.join(g.BASIS, "meine-ergebnisse", "dashboard-daten")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "wachstum.js"), "w", encoding="utf-8") as f:
    f.write("/* erzeugt von skripte/wachstum.py, nicht von Hand ändern */\n")
    f.write("const WACHSTUM_DATEN = " + json.dumps(daten, ensure_ascii=False, separators=(",", ":")) + ";\n")


# ---- Kontrollzahlen ----
def summe(filt):
    w = defaultdict(lambda: [0.0, 0.0, 0])
    for z in zeilen_liste:
        if filt(z):
            w[z[0]][0] += z[4]
            w[z[0]][1] += z[5]
            w[z[0]][2] += z[6]
    return w


def ampel(a, b):
    if a[2] < 20 or b[2] < 20 or not a[1]:
        return "Lücke"
    d = b[1] / a[1] - 1
    return "Wachstum" if d > 0.05 else ("Rückgang" if d < -0.05 else "stabil")


print("Zeilen in wachstum.js:", len(zeilen_liste))
ges = summe(lambda z: True)
ges_ohne = summe(lambda z: z[3] != 2)
print("Gesamt 2025/2026 Liter:", g.de(ges[2025][0]), g.de(ges[2026][0]), " ohne Notfall:", g.de(ges_ohne[2025][0]), g.de(ges_ohne[2026][0]))

print("\nAmpel je Segment (Veränderung Nettoumsatz 2026 gegen 2025, Konzernkurs; Positionen 2025/2026):")
segs = sorted(set(k["segment"] for k in daten["kunden"]))
for s in segs:
    f = lambda z, s=s: daten["kunden"][z[1]]["segment"] == s
    f2 = lambda z, s=s: daten["kunden"][z[1]]["segment"] == s and z[3] != 2
    a, b = summe(f)[2025], summe(f)[2026]
    a2, b2 = summe(f2)[2025], summe(f2)[2026]
    d = "{:+.1f} %".format((b[1] / a[1] - 1) * 100) if a[1] else "–"
    d2 = "{:+.1f} %".format((b2[1] / a2[1] - 1) * 100) if a2[1] else "–"
    print("{:<24} {:>10} -> {:>10} EUR  Pos {:>3}/{:<3} {:>8} {:<9} | ohne Notfall {:>8} {}".format(
        s, g.de(a[1]), g.de(b[1]), a[2], b[2], d, ampel(a, b), d2, ampel(a2, b2)))
print("\nAmpel je Vertriebsweg:")
for i, w in enumerate(WEGE):
    f = lambda z, i=i: z[2] == i
    a, b = summe(f)[2025], summe(f)[2026]
    d = "{:+.1f} %".format((b[1] / a[1] - 1) * 100) if a[1] else "–"
    print("{:<16} {:>10} -> {:>10} EUR  Pos {:>3}/{:<3} {:>8} {}".format(w, g.de(a[1]), g.de(b[1]), a[2], b[2], d, ampel(a, b)))

print("\nTop-5-Anteil am Nettoumsatz (Händler = ein Kunde, Konzernkurs des Jahres):")
for jahr in (2025, 2026):
    for label, filt in (("mit Notfall", lambda z: True), ("ohne Notfall", lambda z: z[3] != 2)):
        je = defaultdict(float)
        for z in zeilen_liste:
            if z[0] == jahr and filt(z):
                je[kunden_ids[z[1]]] += z[5]
        gesamt = sum(je.values())
        top = sorted(je.items(), key=lambda t: -t[1])[:5]
        print(jahr, label, "Top 5 = EUR", g.de(sum(v for _, v in top), 2), "von", g.de(gesamt, 2), "=", "{:.1f} %".format(sum(v for _, v in top) / gesamt * 100),
              [k for k, _ in top])

print("\nNachfüllanteil am Absatz (Liter Nachfüllung / Liter gesamt):")
for jahr in (2025, 2026):
    nf = sum(z[4] for z in zeilen_liste if z[0] == jahr and z[3] == 0)
    al = sum(z[4] for z in zeilen_liste if z[0] == jahr)
    print(jahr, g.de(nf), "/", g.de(al), "=", "{:.1f} %".format(nf / al * 100))
