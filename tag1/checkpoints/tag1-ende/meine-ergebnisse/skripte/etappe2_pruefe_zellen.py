# Etappe 2, Vorprüfung: passen Budget-Zellen (Produktlinie x Segment) und Ist-Zellen zusammen?
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin, absatz
from kern import lese_csv

pos, stat = lade_fin()
plan = defaultdict(lambda: {"l": 0.0, "u": 0.0, "db": 0.0})
for r in lese_csv("budget_2026.csv"):
    z = plan[(r["produktlinie"], r["segment"])]
    z["l"] += float(r["menge_l"])
    z["u"] += float(r["umsatz_eur"])
    z["db"] += float(r["db_eur"])
ist = defaultdict(lambda: {"l": 0.0, "u": 0.0, "n": 0})
for p in pos:
    if p["jahr"] != 2026 or p["vertriebsweg"] == "Notfallservice":
        continue
    z = ist[(p["linie"], p["segment"])]
    z["n"] += 1
    if absatz(p):
        z["l"] += p["liter"]
    z["u"] += p["umsatz"]
print("Plan-Zellen:", len(plan), " Ist-Zellen:", len(ist))
print("Plan gesamt: Liter {:.0f} Umsatz {:.2f} DB {:.2f}".format(
    sum(z["l"] for z in plan.values()), sum(z["u"] for z in plan.values()), sum(z["db"] for z in plan.values())))
print("Ist-Zellen ohne Plan:")
for k in sorted(ist):
    if k not in plan:
        print("  ", k, ist[k])
print("Plan-Zellen ohne Ist:")
for k in sorted(plan):
    if k not in ist:
        print("  ", k, plan[k])
print("Monate je Plan-Zelle (Beispiel Anzahl Zeilen):", len(lese_csv("budget_2026.csv")))
