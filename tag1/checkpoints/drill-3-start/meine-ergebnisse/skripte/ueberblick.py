# -*- coding: utf-8 -*-
"""Reiter „Überblick“: rechnet aus den Tabellen und schreibt dashboard-daten/ueberblick.js.

Aufruf: python meine-ergebnisse/skripte/ueberblick.py

Der Browser rechnet bei jedem Filter neu aus den hier geschriebenen Zeilen (Summen und Zähler,
nie gemittelte Quoten). Zahlen hier = Kontrolle für den Chat.
"""
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g

pos, stat = g.positionen()
kd = g.kunden()
ls = g.lieferstellen()

LAENDER = {"DE": "Deutschland", "AT": "Österreich", "NL": "Niederlande", "PL": "Polen",
           "NO": "Norwegen", "GB": "Großbritannien", "CH": "Schweiz"}
ANWENDUNGEN = {"stationaere_anlage": "stationäre Anlage", "feuerwehrfahrzeug": "Feuerwehrfahrzeug",
               "lager_bestand": "Lagerbestand", "uebung_training": "Übung und Training",
               "tragbarer_feuerloescher": "tragbarer Feuerlöscher", "fahrbarer_feuerloescher": "fahrbarer Feuerlöscher"}
WEGE = ["direkt", "Händler", "Rahmenvertrag", "Notfallservice"]

kunden_ids = sorted(kd)
kidx = {k: i for i, k in enumerate(kunden_ids)}
segmente = sorted(set(v["segment"] for v in kd.values()))
laender = sorted(set(v["land"] for v in kd.values()), key=lambda c: LAENDER[c])
anw_codes = list(ANWENDUNGEN)
ls_ids = sorted(ls)
lidx = {k: i for i, k in enumerate(ls_ids)}

# ---- Zeilen: Jahr x Kunde x Lieferstelle x Vertriebsweg (ohne Muster) ----
zeilen = defaultdict(lambda: [0.0, 0.0, 0])
for p in pos:
    if p["muster"]:
        continue
    key = (p["jahr"], kidx[p["kunde"]], lidx[p["ls"]], WEGE.index(p["vw"]))
    z = zeilen[key]
    z[0] += p["liter"]
    z[1] += p["eur"]
    z[2] += 1
zeilen_liste = [[k[0], k[1], k[2], k[3], round(v[0], 1), round(v[1], 4), v[2]] for k, v in sorted(zeilen.items())]

# ---- aktiver Kunde (24 Monate): Tripel Kunde x Lieferstelle x Vertriebsweg mit Lieferung ----
aktiv = set()
for p in pos:
    if p["art"] == "Lieferung" and not p["muster"] and p["ld"] >= g.FENSTER_24M_AB and p["ld"] <= g.STICHTAG:
        aktiv.add((kidx[p["kunde"]], lidx[p["ls"]], WEGE.index(p["vw"])))
aktiv_liste = sorted([list(t) for t in aktiv])

# ---- Lieferstelle x Vertriebsweg (je mindestens eine Lieferung seit 2021) ----
ls_weg = set()
for p in pos:
    if p["art"] == "Lieferung" and not p["muster"]:
        ls_weg.add((lidx[p["ls"]], WEGE.index(p["vw"])))
ls_weg_liste = sorted([list(t) for t in ls_weg])

daten = {
    "stichtag": "28.02.2027",
    "jahre": [2021, 2022, 2023, 2024, 2025, 2026],
    "teiljahr": 2027,
    "fenster24": "01.03.2025 bis 28.02.2027",
    "segmente": segmente,
    "laender": [{"code": c, "name": LAENDER[c]} for c in laender],
    "wege": WEGE,
    "anwendungen": [{"code": c, "name": ANWENDUNGEN[c]} for c in anw_codes],
    "kunden": [{"id": k, "segment": kd[k]["segment"], "land": kd[k]["land"]} for k in kunden_ids],
    "lieferstellen": [{"id": s, "kunde": kidx[ls[s]["kunde_id"]], "anwendung": anw_codes.index(ls[s]["anwendung"])} for s in ls_ids],
    "zeilen": zeilen_liste,
    "aktiv24": aktiv_liste,
    "ls_weg": ls_weg_liste,
}

ziel = os.path.join(g.BASIS, "meine-ergebnisse", "dashboard-daten")
os.makedirs(ziel, exist_ok=True)
with open(os.path.join(ziel, "ueberblick.js"), "w", encoding="utf-8") as f:
    f.write("/* erzeugt von skripte/ueberblick.py, nicht von Hand ändern */\n")
    f.write("const UEBERBLICK_DATEN = " + json.dumps(daten, ensure_ascii=False, separators=(",", ":")) + ";\n")

# ---- Kontrollzahlen für den Chat ----
print("Bereinigung:", stat)
print("Kunden (aktiver Kunde, 24 Monate):", len(set(t[0] for t in aktiv)))
print("Lieferstellen (Tabelle):", len(ls_ids), " davon mit Lieferung seit 2021:", len(set(t[0] for t in ls_weg)))
je_jahr = defaultdict(lambda: [0.0, 0.0, 0])
for z in zeilen_liste:
    je_jahr[z[0]][0] += z[4]
    je_jahr[z[0]][1] += z[5]
    je_jahr[z[0]][2] += z[6]
for j in sorted(je_jahr):
    l, e, n = je_jahr[j]
    print(j, "Absatz l:", g.de(l), " Nettoumsatz EUR:", g.de(e, 2), " Positionen:", n)
l25, e25, _ = je_jahr[2025]
l26, e26, _ = je_jahr[2026]
print("Veränderung 2026 gegen 2025: Absatz {:+.1f} %, Nettoumsatz {:+.1f} %".format((l26 / l25 - 1) * 100, (e26 / e25 - 1) * 100))
print("Konzernkurse 2026:", g.kurse()["2026"])
print("Zeilen in ueberblick.js:", len(zeilen_liste))
# Händler-Kontrolle
h = defaultdict(lambda: [0.0, 0.0, 0])
for z in zeilen_liste:
    if WEGE[z[3]] == "Händler":
        h[z[0]][0] += z[4]
        h[z[0]][1] += z[5]
        h[z[0]][2] += z[6]
print("Händler je Jahr (Liter, EUR, Positionen):", {j: (round(v[0]), round(v[1]), v[2]) for j, v in sorted(h.items())})
print("Kunden mit Händler-Lieferung 24 Monate:", len(set(t[0] for t in aktiv if t[2] == 1)))
