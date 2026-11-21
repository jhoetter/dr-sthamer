# Etappe 3 Drill 2: Rabattquote 2025/2026 je Vertriebsweg, Listenpreiserhöhung, Fremdwährungseffekt je Währung
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin
from preise import rabatt_gruppen, listenpreiserhoehung_2026
from bruecke import fx_je_waehrung


def f0(x):
    return "{:,.0f}".format(x).replace(",", ".")


def pct(x):
    return "Lücke" if x is None else "{:.1f} %".format(x * 100).replace(".", ",")


def d2(x):
    return "{:.2f}".format(x).replace(".", ",")


pos, stat = lade_fin()
g = rabatt_gruppen(pos, lambda p: (p["jahr"], p["vertriebsweg"]))
print("{:<6}{:<16}{:>6}{:>10}{:>12}{:>12}{:>10}{:>9}{:>9}  {}".format(
    "Jahr", "Vertriebsweg", "Pos.", "Liter", "Nettoumsatz", "Listenwert", "Rabatt", "Liste/l", "Real/l", "ohne Liste"))
for k in sorted(g):
    z = g[k]
    q = "Lücke (<20)" if z["n"] < 20 else pct(z["quote"])
    print("{:<6}{:<16}{:>6}{:>10}{:>12}{:>12}{:>10}{:>9}{:>9}  {}".format(
        k[0], k[1], z["n"], f0(z["liter"]), f0(z["netto"]), f0(z["liste"]), q, d2(z["liste_je_l"]), d2(z["real_je_l"]), z["ohne_liste"]))
print()
for jahr in (2025, 2026):
    t = rabatt_gruppen(pos, lambda p, j=jahr: p["jahr"])[jahr]
    print("Gesamt {}: {} Pos., Netto {} / Liste {} -> Rabattquote {}; Liste/l {}, real/l {}".format(
        jahr, t["n"], f0(t["netto"]), f0(t["liste"]), pct(t["quote"]), d2(t["liste_je_l"]), d2(t["real_je_l"])))
a, b, fehlt = listenpreiserhoehung_2026(pos)
print("Listenpreiserhöhung 2026 auf dem Korb der 2026er Lieferungen (ohne Notfall): Liste 2025 {} -> Liste 2026 {}: {} (ohne Listenpreis: {} Pos.)".format(
    f0(a), f0(b), pct(b / a - 1), fehlt))
print()
print("Rabattquote 2026 nach Produktlinie:")
g2 = rabatt_gruppen(pos, lambda p: (p["jahr"], p["linie"]))
for k in sorted(g2):
    z = g2[k]
    print(" ", k, z["n"], "Pos.", pct(z["quote"]) if z["n"] >= 20 else "Lücke (<20)")
print()
print("Fremdwährungseffekt 2026 je Währung (Umsatz = DB-Effekt, ohne Notfallservice; Ist-Betrag in FW x (Ist-Monatskurs - Plankurs))")
for w, z in sorted(fx_je_waehrung(pos).items()):
    print(" ", w, z["n"], "Pos.", "Betrag in FW", f0(z["betrag_fw"]), "Effekt EUR", d2(z["effekt"]))
