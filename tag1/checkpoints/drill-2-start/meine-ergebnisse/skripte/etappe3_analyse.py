# Etappe 3: Fluorfrei-Anteil je Jahr nach Segment und Anwendung, Industrie-Vergleich, Ausreißer, Datenaufnahme
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, lade_positionen, absatz

pos, stat = lade_positionen()
pos = [p for p in pos if absatz(p)]


def per(p):
    return "Jan.-Feb. 2027" if p["jahr"] == 2027 else str(p["jahr"])


def tab(titel, keyf, filt=lambda p: True):
    print("\n==", titel)
    agg = defaultdict(lambda: [0.0, 0.0, 0])
    for p in pos:
        if not filt(p):
            continue
        k = keyf(p)
        a = agg[k]
        a[1] += p["liter"]
        a[2] += 1
        if p["linie"] == "fluorfrei":
            a[0] += p["liter"]
    for k in sorted(agg):
        z, n, c = agg[k]
        txt = "Lücke (<20 Pos.)" if c < 20 else "%.1f %%" % (100 * z / n) if n else "-"
        print("%-48s Z=%9.0f N=%9.0f Pos=%3d  %s" % (str(k), z, n, c, txt))


tab("Gesamt je Periode", lambda p: per(p))
tab("Segment x Periode", lambda p: (p["segment"], per(p)))
tab("Anwendung x Periode", lambda p: (p["anwendung"], per(p)))
tab("2026: Industrie stationär vs. Industrie andere vs. stationär außerhalb Industrie vs. Rest",
    lambda p: ("Industrie" if p["segment"] == "Industrie" else "außerhalb Industrie") + " / " +
              ("stationär" if p["anwendung"] == "stationaere_anlage" else "andere Anwendung"),
    lambda p: p["jahr"] == 2026)
tab("2025 dito",
    lambda p: ("Industrie" if p["segment"] == "Industrie" else "außerhalb Industrie") + " / " +
              ("stationär" if p["anwendung"] == "stationaere_anlage" else "andere Anwendung"),
    lambda p: p["jahr"] == 2025)

# Große Einzellieferungen 2026
print("\n== Größte Positionen 2026 (Liter)")
g26 = sorted([p for p in pos if p["jahr"] == 2026], key=lambda p: -p["liter"])[:8]
for p in g26:
    print(p["auftrag_id"], p["position"], p["datum"], p["kunde_id"], p["segment"], p["anwendung"], p["vertriebsweg"], p["produkt_id"], p["linie"], p["liter"])
liter26 = sum(p["liter"] for p in pos if p["jahr"] == 2026)
print("Notfallservice 2026 Positionen:", [(p["auftrag_id"], p["liter"], p["linie"], p["segment"], p["anwendung"]) for p in pos if p["jahr"] == 2026 and p["vertriebsweg"] == "Notfallservice"])
print("Median Liter/Position 2026:", sorted(p["liter"] for p in pos if p["jahr"] == 2026)[len([1 for p in pos if p["jahr"] == 2026]) // 2])

# Ohne größte Einzellieferung
top = g26[0]
for lab, f in [("mit", lambda p: True), ("ohne größte Position", lambda p: not (p["auftrag_id"] == top["auftrag_id"] and p["position"] == top["position"]))]:
    sel = [p for p in pos if p["jahr"] == 2026 and f(p)]
    z = sum(p["liter"] for p in sel if p["linie"] == "fluorfrei")
    n = sum(p["liter"] for p in sel)
    print("2026 gesamt", lab, z, n, 100 * z / n)
    sel2 = [p for p in sel if p["segment"] == "Industrie"]
    z = sum(p["liter"] for p in sel2 if p["linie"] == "fluorfrei")
    n = sum(p["liter"] for p in sel2)
    print("2026 Industrie", lab, z, n, 100 * z / n)
    sel3 = [p for p in sel if p["segment"] == "Industrie" and p["anwendung"] == "stationaere_anlage"]
    z = sum(p["liter"] for p in sel3 if p["linie"] == "fluorfrei")
    n = sum(p["liter"] for p in sel3)
    print("2026 Industrie stationär", lab, z, n, 100 * z / n if n else None, len(sel3))

# Datenaufnahme stationäre Anlagen
ls = lese_csv("lieferstellen.csv")
st = [r for r in ls if r["anwendung"] == "stationaere_anlage"]
da = [r for r in st if r["datenaufnahme_am"]]
print("\nStationäre Anlagen:", len(st), "davon mit Datenaufnahme:", len(da))
kunden = {r["id"]: r for r in lese_csv("kunden.csv")}
print("nach Segment (stationär / mit DA):")
seg = defaultdict(lambda: [0, 0])
for r in st:
    s = kunden[r["kunde_id"]]["segment"]
    seg[s][0] += 1
    if r["datenaufnahme_am"]:
        seg[s][1] += 1
print(dict(seg))
