# -*- coding: utf-8 -*-
"""Zahlen für die Beiratspräsentation (Drill 5), frisch aus den Tabellen.

Aufruf: python meine-ergebnisse/skripte/praesentation_zahlen.py
Schreibt meine-ergebnisse/skripte/d5/praesentation_zahlen.json und gibt die Kontrollzahlen aus.
Regeln: Doppelimporte einmal, Muster ohne Absatz, Gutschriften/Retouren abgezogen (negative Mengen),
Absatz in Litern nach Lieferdatum, Nettoumsatz in EUR zum Konzernkurs des Lieferjahres.
"""
import json
import os
import sys
from collections import defaultdict
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g

pos, stat = g.positionen()
kd = g.kunden()
JAHRE = [2021, 2022, 2023, 2024, 2025, 2026]

# Absatz und Positionen je Jahr und Auftragsart (ohne Muster)
liter = defaultdict(float)
eur = defaultdict(float)
anz = defaultdict(int)
for p in pos:
    if p["muster"]:
        continue
    for key in ((p["jahr"], p["art_auftrag"]), (p["jahr"], "Gesamt")):
        liter[key] += p["liter"]
        eur[key] += p["eur"]
        anz[key] += 1

zeitreihe = {}
for j in JAHRE:
    gesamt = liter[(j, "Gesamt")]
    notfall = liter[(j, "Notfall")]
    zeitreihe[j] = {
        "gesamt_l": round(gesamt, 1), "gesamt_pos": anz[(j, "Gesamt")],
        "notfall_l": round(notfall, 1), "notfall_pos": anz[(j, "Notfall")],
        "ohne_notfall_l": round(gesamt - notfall, 1), "ohne_notfall_pos": anz[(j, "Gesamt")] - anz[(j, "Notfall")],
        "nachfuell_l": round(liter[(j, "Nachfüllung")], 1), "nachfuell_pos": anz[(j, "Nachfüllung")],
        "erst_l": round(liter[(j, "Erstbefüllung")], 1), "erst_pos": anz[(j, "Erstbefüllung")],
        "gesamt_eur": round(eur[(j, "Gesamt")], 2), "nachfuell_eur": round(eur[(j, "Nachfüllung")], 2),
    }

print("Absatz in Litern (netto, ohne Muster) und Positionen:")
for j in JAHRE:
    z = zeitreihe[j]
    print(j, "Gesamt", g.de(z["gesamt_l"]), "(", z["gesamt_pos"], ") | ohne Notfall", g.de(z["ohne_notfall_l"]),
          "| Nachfüllung", g.de(z["nachfuell_l"]), "(", z["nachfuell_pos"], ") | Erstbefüllung", g.de(z["erst_l"]), "(", z["erst_pos"], ")",
          "| Notfall", g.de(z["notfall_l"]), "(", z["notfall_pos"], ")")

a, b = zeitreihe[2025], zeitreihe[2026]
print("\nWachstum 2026 gegen 2025:")
print("Gesamt {:+.2f} %  ({} -> {})".format((b["gesamt_l"] / a["gesamt_l"] - 1) * 100, g.de(a["gesamt_l"]), g.de(b["gesamt_l"])))
print("ohne Notfall {:+.2f} %  ({} -> {})".format((b["ohne_notfall_l"] / a["ohne_notfall_l"] - 1) * 100, g.de(a["ohne_notfall_l"]), g.de(b["ohne_notfall_l"])))
print("Nachfüllung Liter {:+.2f} %  Umsatz {:+.2f} % (EUR {} -> {})".format(
    (b["nachfuell_l"] / a["nachfuell_l"] - 1) * 100, (b["nachfuell_eur"] / a["nachfuell_eur"] - 1) * 100,
    g.de(a["nachfuell_eur"]), g.de(b["nachfuell_eur"])))
print("Nachfüllanteil am Absatz 2025 {:.1f} %, 2026 {:.1f} %".format(
    a["nachfuell_l"] / a["gesamt_l"] * 100, b["nachfuell_l"] / b["gesamt_l"] * 100))
print("Nachfüllanteil ohne Notfall 2026 {:.1f} %".format(b["nachfuell_l"] / b["ohne_notfall_l"] * 100))

# Kundenstatus nach letzter Lieferung (art = Lieferung), Stichtag 28.02.2027
letzte = {}
for p in pos:
    if p["art"] != "Lieferung":
        continue
    if p["kunde"] not in letzte or p["ld"] > letzte[p["kunde"]]:
        letzte[p["kunde"]] = p["ld"]
grenze_aktiv = date(2026, 3, 1)
grenze_ruhend = date(2025, 3, 1)
status = defaultdict(list)
for k in sorted(kd):
    ld = letzte.get(k)
    if ld is None or ld < grenze_ruhend:
        status["verloren"].append(k)
    elif ld < grenze_aktiv:
        status["ruhend"].append(k)
    else:
        status["aktiv"].append(k)
print("\nKundenstatus (Stichtag 28.02.2027, {} Kunden im Übungsausschnitt):".format(len(kd)))
for s in ("aktiv", "ruhend", "verloren"):
    print(s, len(status[s]), status[s])

# Top-5-Anteil am Nettoumsatz (Händler = ein Kunde)
top5 = {}
print("\nTop-5-Anteil am Nettoumsatz:")
for jahr in (2025, 2026):
    for label, ohne in (("mit Notfall", False), ("ohne Notfall", True)):
        je = defaultdict(float)
        for p in pos:
            if p["muster"] or p["jahr"] != jahr:
                continue
            if ohne and p["art_auftrag"] == "Notfall":
                continue
            je[p["kunde"]] += p["eur"]
        gesamt = sum(je.values())
        top = sorted(je.items(), key=lambda t: -t[1])[:5]
        zaehler = sum(v for _, v in top)
        top5["%d %s" % (jahr, label)] = {"zaehler": round(zaehler, 2), "nenner": round(gesamt, 2), "anteil": round(zaehler / gesamt * 100, 2), "kunden": [k for k, _ in top]}
        print(jahr, label, "EUR", g.de(zaehler, 2), "/", g.de(gesamt, 2), "= {:.1f} %".format(zaehler / gesamt * 100), [k for k, _ in top])

ziel = os.path.join(g.BASIS, "meine-ergebnisse", "skripte", "d5")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "praesentation_zahlen.json"), "w", encoding="utf-8") as f:
    json.dump({"zeitreihe": zeitreihe, "kundenstatus": {k: len(v) for k, v in status.items()}, "top5": top5}, f, ensure_ascii=False, indent=1)
