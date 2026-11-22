# -*- coding: utf-8 -*-
"""Belegzahlen für den Finanzkommentar (nur Ausgabe im Chat)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bruecke as br
import finanz_basis as fb
import gemeinsam as g

r = br.rechne()
u_ist_monat_ohne = sum(w["u_monat"] for w in r["ist"].values())
print("Ist ohne Notfall, Ist-Monatskurse: Umsatz", g.de(u_ist_monat_ohne, 2), "DB", g.de(r["ist_db_zellen"], 2), "Marge {:.3f} %".format(r["ist_db_zellen"] / u_ist_monat_ohne * 100))
print("Budget: Umsatz", g.de(r["Up"], 2), "DB", g.de(r["DBp"], 2), "Marge {:.3f} %".format(r["DBp"] / r["Up"] * 100))
print("Ist mit Notfall, Monatskurse: Umsatz", g.de(r["ist_u_monat"], 2), "DB", g.de(r["ist_db_gesamt"], 2), "Marge {:.3f} %".format(r["ist_db_gesamt"] / r["ist_u_monat"] * 100))
print("Abweichung ohne Notfall: {} ({:.2f} %)".format(g.de(r["ist_db_zellen"] - r["DBp"], 2), (r["ist_db_zellen"] / r["DBp"] - 1) * 100))
print("Abweichung mit Notfall: {} ({:.2f} %)".format(g.de(r["gesamtabw"], 2), r["gesamtabw"] / r["DBp"] * 100))
print("Liter: Ist ohne Notfall", g.de(r["Qi"]), "Plan", g.de(r["Qp"]), "Differenz", g.de(r["Qi"] - r["Qp"]), "({:.1f} %)".format((r["Qi"] / r["Qp"] - 1) * 100))
print("Umsatz Ist ohne Notfall Monatskurse vs Budget: {} ({:.1f} %)".format(g.de(u_ist_monat_ohne - r["Up"], 2), (u_ist_monat_ohne / r["Up"] - 1) * 100))

pos = r["pos"]
print("\nVertriebsweg (Ist, Konzernkurs des Jahres):")
for jahr in (2025, 2026):
    s = fb.summiere(pos, lambda p: p["vw"], jahr, filt=lambda p: not p["muster"] or True)
    for k in sorted(s):
        w = s[k]
        n_ohne_muster = sum(1 for p in pos if p["jahr"] == jahr and p["vw"] == k and not p["muster"])
        print(jahr, "{:<15} Umsatz {:>12} DB {:>12} Marge {:>6.2f} % Pos(ohne Muster) {}".format(k, g.de(w["umsatz"], 2), g.de(w["db"], 2), w["marge"] * 100, n_ohne_muster))
print("\nPlan-Marge je Vertriebsweg (Budget, Plankurs):")
for weg in br.WEGE_PLAN:
    u = sum(w["u"] for c, w in r["plan"].items() if c[1] == weg)
    d = sum(w["db"] for c, w in r["plan"].items() if c[1] == weg)
    print(" ", weg, "Umsatz", g.de(u, 2), "DB", g.de(d, 2), "Marge {:.2f} %".format(d / u * 100))
