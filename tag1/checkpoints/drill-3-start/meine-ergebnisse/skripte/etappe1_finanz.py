# Etappe 1 Drill 2: Nettoumsatz, Herstellkosten, Fracht, DB, DB-Marge 2025 und 2026
# je Produktlinie und je Segment; dazu Notfallservice-Nachhaken. Alle Beträge EUR, Konzernkurs des Lieferjahres.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin, summiere


def f(x):
    return "{:,.0f}".format(x).replace(",", ".")


def pct(x):
    return "Lücke" if x is None else "{:.1f} %".format(x * 100).replace(".", ",")


def zeile(name, z):
    kleine = z["n"] < 20
    m = "Lücke (<20 Pos.)" if kleine else pct(z["marge"])
    return "{:<34}{:>5}{:>11}{:>12}{:>12}{:>10}{:>12}  {}".format(
        name, z["n"], f(z["liter"]), f(z["umsatz"]), f(z["herst"]), f(z["fracht"]), f(z["db"]), m)


KOPF = "{:<34}{:>5}{:>11}{:>12}{:>12}{:>10}{:>12}  {}".format(
    "Gruppe", "Pos.", "Liter", "Nettoumsatz", "Herstellk.", "Fracht", "DB", "DB-Marge")

pos, stat = lade_fin()
print("Bereinigung:", dict(stat))
print()

for jahr in (2025, 2026):
    filt = (lambda p, j=jahr: p["jahr"] == j)
    print("=== Jahr", jahr, "(EUR, netto, Konzernkurs des Jahres) ===")
    print(KOPF)
    g = summiere(pos, lambda p: "gesamt", filt)
    print(zeile("GESAMT", g["gesamt"]))
    g = summiere(pos, lambda p: p["linie"], filt)
    for k in sorted(g):
        print(zeile("Linie " + k, g[k]))
    g = summiere(pos, lambda p: (p["linie"], p["segment"]), filt)
    for k in sorted(g):
        print(zeile("  " + k[0] + " / " + k[1], g[k]))
    print()

# Muster, Gutschriften, Retouren 2025/2026
print("=== Sonderarten (Positionen, Liter, Umsatz, Herstellkosten, Fracht) ===")
g = summiere(pos, lambda p: (p["jahr"], p["art"]), lambda p: p["jahr"] in (2025, 2026) and p["art"] != "Lieferung")
for k in sorted(g):
    z = g[k]
    print(k, z["n"], f(z["liter"]), f(z["umsatz"]), f(z["herst"]), f(z["fracht"]))
print()

# Notfallservice
print("=== Notfallservice (Vertriebsweg) ===")
g = summiere(pos, lambda p: (p["jahr"], p["vertriebsweg"] == "Notfallservice", p["linie"]),
             lambda p: p["jahr"] in (2025, 2026))
for k in sorted(g):
    if k[1]:
        print(k, zeile("  Notfall " + k[2], g[k]))
print()
print("Marge fluorhaltig 2026 mit und ohne Notfallservice:")
for name, filt in (("mit", lambda p: p["jahr"] == 2026 and p["linie"] == "fluorhaltig"),
                   ("ohne", lambda p: p["jahr"] == 2026 and p["linie"] == "fluorhaltig"
                    and p["vertriebsweg"] != "Notfallservice")):
    g = summiere(pos, lambda p: "x", filt)["x"]
    print(zeile(name + " Notfallservice", g))
print("Gesamt 2026 ohne Notfallservice:")
g = summiere(pos, lambda p: "x", lambda p: p["jahr"] == 2026 and p["vertriebsweg"] != "Notfallservice")["x"]
print(zeile("Gesamt ohne Notfall", g))
print()
# große Notfallpositionen
for p in pos:
    if p["vertriebsweg"] == "Notfallservice" and p["jahr"] == 2026:
        print("Notfall:", p["datum"], p["auftrag_id"], p["kunde_id"], p["produkt_id"], p["linie"], p["art"],
              f(p["liter"]), "l", f(p["umsatz"]), "EUR")
