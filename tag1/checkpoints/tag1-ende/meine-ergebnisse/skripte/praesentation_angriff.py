# Rückfragen des externen Beiratsmitglieds: Empfindlichkeit der Zahlen (nur lesen, nichts ändern)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lade_positionen, absatz as absatz_k
from fin_kern import lade_fin, summiere

pos, _ = lade_positionen()


def liter(jahr, linie=None, ohne_notfall=False):
    z = 0.0
    for p in pos:
        if p["jahr"] != jahr or not absatz_k(p):
            continue
        if linie and p["linie"] != linie:
            continue
        if ohne_notfall and p["vertriebsweg"] == "Notfallservice":
            continue
        z += p["liter"]
    return z


for j in (2025, 2026):
    print(j, "alle Liter", liter(j), "fluorfrei", liter(j, "fluorfrei"), "fluorhaltig", liter(j, "fluorhaltig"),
          "offen", liter(j, "offen"))
a, b = liter(2025), liter(2026)
print("alle Liter 2026 gegen 2025: %.1f %%" % (100 * (b / a - 1)))
a, b = liter(2025, "fluorfrei"), liter(2026, "fluorfrei")
print("fluorfreie Liter 2026 gegen 2025: %.1f %%" % (100 * (b / a - 1)))
a, b = liter(2025, "fluorhaltig"), liter(2026, "fluorhaltig")
print("fluorhaltige Liter 2026 gegen 2025: %.1f %%" % (100 * (b / a - 1)))
print("fluorfrei-Anteil 2026 ohne Notfalllieferung: %.1f %% (%s von %s l)" %
      (100 * liter(2026, "fluorfrei", True) / liter(2026, None, True), liter(2026, "fluorfrei", True), liter(2026, None, True)))

fpos, _ = lade_fin()
for name, jahr, linie, nf in [("fluorfrei 2026", 2026, "fluorfrei", None), ("fluorhaltig 2026 ohne NF", 2026, "fluorhaltig", False),
                              ("fluorfrei 2025", 2025, "fluorfrei", None), ("fluorhaltig 2025", 2025, "fluorhaltig", None)]:
    s = summiere(fpos, lambda p: p["linie"], lambda p: p["jahr"] == jahr and (nf is None or (p["vertriebsweg"] == "Notfallservice") == nf))[linie]
    vor_fracht = (s["umsatz"] - s["herst"]) / s["umsatz"]
    print(name, "Umsatz %.0f Herst %.0f Fracht %.0f | Marge nach Herst+Fracht %.1f %% | nur nach Herstellkosten %.1f %% | Fracht %.1f %% vom Umsatz" %
          (s["umsatz"], s["herst"], s["fracht"], 100 * s["marge"], 100 * vor_fracht, 100 * s["fracht"] / s["umsatz"]))
