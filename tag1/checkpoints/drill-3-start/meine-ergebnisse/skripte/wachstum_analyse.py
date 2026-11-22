# -*- coding: utf-8 -*-
"""Drill 1, Etappe 3: Analyse 2026 gegen 2025 (nur Ausgabe im Chat, noch nichts im Dashboard)."""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g

pos, stat = g.positionen()
kd = g.kunden()
ls = g.lieferstellen()


def tabelle(titel, schluessel, filt=None):
    print("\n" + titel)
    w = defaultdict(lambda: defaultdict(lambda: [0.0, 0.0, 0]))
    for p in pos:
        if p["muster"] or p["jahr"] not in (2025, 2026):
            continue
        if filt and not filt(p):
            continue
        z = w[schluessel(p)][p["jahr"]]
        z[0] += p["liter"]
        z[1] += p["eur"]
        z[2] += 1
    print("{:<26}{:>10}{:>10}{:>9}{:>9}{:>12}{:>12}{:>9}{:>7}{:>7}".format(
        "Gruppe", "l 2025", "l 2026", "Δ l", "Δ %", "EUR 2025", "EUR 2026", "Δ EUR %", "n25", "n26"))
    ges = {2025: [0, 0, 0], 2026: [0, 0, 0]}
    for gr in sorted(w):
        a, b = w[gr][2025], w[gr][2026]
        for j, z in ((2025, a), (2026, b)):
            for i in range(3):
                ges[j][i] += z[i]
        dl = b[0] - a[0]
        pl = "{:+.1f}".format((b[0] / a[0] - 1) * 100) if a[0] else "–"
        pe = "{:+.1f}".format((b[1] / a[1] - 1) * 100) if a[1] else "–"
        print("{:<26}{:>10}{:>10}{:>9}{:>9}{:>12}{:>12}{:>9}{:>7}{:>7}".format(
            gr, g.de(a[0]), g.de(b[0]), g.de(dl), pl, g.de(a[1]), g.de(b[1]), pe, a[2], b[2]))
    a, b = ges[2025], ges[2026]
    print("{:<26}{:>10}{:>10}{:>9}{:>9}{:>12}{:>12}{:>9}{:>7}{:>7}".format(
        "GESAMT", g.de(a[0]), g.de(b[0]), g.de(b[0] - a[0]), "{:+.1f}".format((b[0] / a[0] - 1) * 100),
        g.de(a[1]), g.de(b[1]), "{:+.1f}".format((b[1] / a[1] - 1) * 100), a[2], b[2]))


tabelle("Nach Auftragsart (Positionen inkl. Gutschriften/Retouren, ohne Muster)", lambda p: p["art_auftrag"])
tabelle("Nach Vertriebsweg", lambda p: p["vw"])
tabelle("Nach Auftragsart und Art (Zerlegung Lieferung/Gutschrift/Retoure)", lambda p: p["art_auftrag"] + " / " + p["art"])
tabelle("Nach Segment (mit Notfall)", lambda p: kd[p["kunde"]]["segment"])
tabelle("Nach Segment OHNE Notfalllieferung", lambda p: kd[p["kunde"]]["segment"], lambda p: p["art_auftrag"] != "Notfall")

print("\nErstbefüllungen 2025 und 2026 einzeln (Lieferungen, Gutschriften, Retouren):")
print("{:<14}{:<6}{:<12}{:<9}{:<42}{:<24}{:>9}{:>12}".format("Auftrag", "Pos", "Lieferdatum", "Kunde", "Anlage", "Anwendung", "Liter", "EUR"))
for p in sorted(pos, key=lambda p: p["ld"]):
    if p["art_auftrag"] == "Erstbefüllung" and p["jahr"] in (2025, 2026):
        print("{:<14}{:<6}{:<12}{:<9}{:<42}{:<24}{:>9}{:>12} {}".format(
            p["auftrag_id"], p["position"], str(p["ld"]), p["kunde"], ls[p["ls"]]["anlage"][:40], p["anwendung"],
            g.de(p["liter"]), g.de(p["eur"], 2), p["art"]))

print("\nErstbefüllungen je Jahr 2021–2026 (Liter netto / Positionen):")
j = defaultdict(lambda: [0.0, 0])
for p in pos:
    if p["art_auftrag"] == "Erstbefüllung" and not p["muster"]:
        j[p["jahr"]][0] += p["liter"]
        j[p["jahr"]][1] += 1
for y in sorted(j):
    print(y, g.de(j[y][0]), j[y][1])

print("\nNotfalllieferungen (alle Jahre):")
for p in sorted(pos, key=lambda p: p["ld"]):
    if p["art_auftrag"] == "Notfall":
        print(p["auftrag_id"], p["position"], p["ld"], p["kunde"], kd[p["kunde"]]["name"], kd[p["kunde"]]["segment"], g.de(p["liter"]), "l", "EUR", g.de(p["eur"], 2), p["vw"], p["art"])

print("\nNachfüllung je Jahr 2021–2026 (Liter / Positionen):")
j = defaultdict(lambda: [0.0, 0])
for p in pos:
    if p["art_auftrag"] == "Nachfüllung" and not p["muster"]:
        j[p["jahr"]][0] += p["liter"]
        j[p["jahr"]][1] += 1
for y in sorted(j):
    print(y, g.de(j[y][0]), j[y][1])

print("\nGutschriften/Retouren 2026 in der Nachfüllung (Positionen, Liter, EUR):")
for art in ("Gutschrift", "Retoure"):
    sel = [p for p in pos if p["jahr"] == 2026 and p["art_auftrag"] == "Nachfüllung" and p["art"] == art]
    print(art, len(sel), g.de(sum(p["liter"] for p in sel)), g.de(sum(p["eur"] for p in sel), 2))
sel = [p for p in pos if p["jahr"] == 2026 and p["art_auftrag"] == "Nachfüllung" and p["art"] == "Lieferung" and not p["muster"]]
print("Nachfüllung 2026 Lieferungen:", len(sel), g.de(sum(p["liter"] for p in sel)))
