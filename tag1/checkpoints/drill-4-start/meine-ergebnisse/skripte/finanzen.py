# Reiter „Finanzen“: erzeugt dashboard-daten/finanzen.js
# Definitionen: kennzahlen.json -> deckungsbeitrag, umrechnung_fremdwaehrung, rabattquote, plan_ist_bruecke
import json
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin, absatz
from bruecke import bruecke, fx_je_waehrung, plan_zellen
from preise import rabatt_gruppen, listenpreiserhoehung_2026
from kern import BASIS, KURSE, lese_csv

pos, stat = lade_fin()

# 1) Zellen Jahr x Produktlinie x Segment x Notfallservice (Konzernkurs des Lieferjahres); Marge wird im Browser aus Summen gerechnet
z = defaultdict(lambda: {"n": 0, "l": 0.0, "u": 0.0, "h": 0.0, "f": 0.0})
for p in pos:
    if p["jahr"] not in (2025, 2026):
        continue
    k = (p["jahr"], p["linie"], p["segment"], p["vertriebsweg"] == "Notfallservice")
    c = z[k]
    c["n"] += 1
    if absatz(p):
        c["l"] += p["liter"]
    c["u"] += p["umsatz"]
    c["h"] += p["herst"]
    c["f"] += p["fracht"]
zellen = [{"j": k[0], "linie": k[1], "seg": k[2], "nf": k[3], "n": v["n"], "l": round(v["l"], 2),
           "u": round(v["u"], 2), "h": round(v["h"], 2), "f": round(v["f"], 2)} for k, v in sorted(z.items())]

# 2) Brücken
br = {}
for w in ("u", "db"):
    b = bruecke(pos, w)
    br[w] = {k: round(v, 2) for k, v in b.items()}
    if abs(b["differenz"]) > 0.005:
        raise SystemExit("Brücke geht nicht auf: " + w + " " + str(b["differenz"]))

plan = plan_zellen()
plan_u = sum(c["u"] for c in plan.values())
plan_db = sum(c["db"] for c in plan.values())
plan_l = sum(c["l"] for c in plan.values())

# 3) Preise: Rabattquote je Jahr und Vertriebsweg (ohne Notfallservice)
g = rabatt_gruppen(pos, lambda p: (p["jahr"], p["vertriebsweg"]))
preise = []
for k in sorted(g):
    v = g[k]
    preise.append({"j": k[0], "weg": k[1], "n": v["n"], "l": round(v["liter"], 2), "netto": round(v["netto"], 2),
                   "liste": round(v["liste"], 2)})
a, b, fehlt = listenpreiserhoehung_2026(pos)

# 4) Fremdwährung je Währung
fx = [{"w": w, "n": v["n"], "betrag_fw": round(v["betrag_fw"], 2), "effekt": round(v["effekt"], 2)}
      for w, v in sorted(fx_je_waehrung(pos).items())]

# 5) Notfallservice 2026 (Angaben für Text und Tooltip) und Plankurse
nf = [p for p in pos if p["jahr"] == 2026 and p["vertriebsweg"] == "Notfallservice"]
notfall = {"n": len(nf), "datum": nf[0]["datum"] if nf else "", "liter": round(sum(p["liter"] for p in nf), 2)}
plankurse = {}
for r in lese_csv("kurse.csv"):
    plankurse[r["waehrung"]] = float(r["plankurs_eur"])

daten = {
    "notfall": notfall,
    "plankurse": plankurse,
    "stichtag": "28.02.2027",
    "zellen": zellen,
    "bruecke": br,
    "budget": {"umsatz": round(plan_u, 2), "db": round(plan_db, 2), "liter": plan_l,
               "marge": plan_db / plan_u},
    "preise": preise,
    "liste_korb": {"liste25": round(a, 2), "liste26": round(b, 2)},
    "fx": fx,
    "kurse2026": KURSE["2026"],
    "pruefung": {"fracht_tabelle": stat["fracht_summe_tabelle"], "fracht_verteilt": stat["fracht_summe_verteilt"],
                 "doppelt": stat["doppelt"], "muster": stat["Muster"], "gutschriften": stat["Gutschrift"],
                 "retouren": stat["Retoure"]},
}
ziel = os.path.join(BASIS, "meine-ergebnisse", "dashboard-daten", "finanzen.js")
with open(ziel, "w", encoding="utf-8") as f:
    f.write("/* erzeugt von skripte/finanzen.py – nicht von Hand ändern */\nvar FINANZEN = ")
    json.dump(daten, f, ensure_ascii=False, separators=(",", ":"))
    f.write(";\n")
print("geschrieben:", ziel, "Zellen:", len(zellen), "Preisgruppen:", len(preise))
print("Brücke Umsatz Differenz:", br["u"]["differenz"], " Brücke DB Differenz:", br["db"]["differenz"])
