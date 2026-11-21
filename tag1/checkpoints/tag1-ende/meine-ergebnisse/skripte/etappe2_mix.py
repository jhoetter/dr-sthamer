# Etappe 2 Nachhaken: Mix-Effekt je Zelle (Umsatz und DB) und Liter/Fluorfrei-Anteil Plan gegen Ist 2026
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin
from bruecke import plan_zellen, ist_zellen


def f0(x):
    return "{:,.0f}".format(x).replace(",", ".")


def f2(x):
    return "{:,.2f}".format(x).replace(",", "X").replace(".", ",").replace("X", ".")


pos, stat = lade_fin()
plan = plan_zellen()
ist = ist_zellen(pos, notfall=False)
Lp = sum(z["l"] for z in plan.values())
Li = sum(z["l"] for z in ist.values())
Up = sum(z["u"] for z in plan.values())
Dp = sum(z["db"] for z in plan.values())
avg_u, avg_d = Up / Lp, Dp / Lp

print("Plan: {} l, Umsatz {}, DB {}; Ø Umsatz/l {:.4f}, Ø DB/l {:.4f}".format(f0(Lp), f2(Up), f2(Dp), avg_u, avg_d))
print("Ist (ohne Notfall): {} l".format(f0(Li)))
print()
print("{:<40}{:>9}{:>9}{:>8}{:>8}{:>8}{:>12}{:>12}".format(
    "Zelle (Linie / Segment)", "Plan l", "Ist l", "U/l P", "DB/l P", "DB/l-Ø", "Mix Umsatz", "Mix DB"))
mu_sum = md_sum = 0.0
for k in sorted(plan):
    p = plan[k]
    i = ist.get(k, {"l": 0.0})
    uj, dj = p["u"] / p["l"], p["db"] / p["l"]
    # Beitrag der Zelle zum Mixeffekt: Ist-Liter x (Plan-Wert je Liter - Plan-Durchschnitt)
    mu = i["l"] * (uj - avg_u)
    md = i["l"] * (dj - avg_d)
    mu_sum += mu
    md_sum += md
    print("{:<40}{:>9}{:>9}{:>8.2f}{:>8.2f}{:>8.2f}{:>12}{:>12}".format(
        k[0] + " / " + k[1], f0(p["l"]), f0(i["l"]), uj, dj, dj - avg_d, f2(mu), f2(md)))
print("Summe Mix (Umsatz) {} · Summe Mix (DB) {}".format(f2(mu_sum), f2(md_sum)))
print()


def anteil(zellen, linie):
    l = sum(z["l"] for k, z in zellen.items() if k[0] == linie)
    return l


for name, z in (("Plan", plan), ("Ist ohne Notfall", ist)):
    ff, fh, of = anteil(z, "fluorfrei"), anteil(z, "fluorhaltig"), anteil(z, "offen")
    ges = ff + fh + of
    print("{}: fluorfrei {} l, fluorhaltig {} l, offen {} l, gesamt {} l -> Fluorfrei-Anteil {:.1f} %".format(
        name, f0(ff), f0(fh), f0(of), f0(ges), 100 * ff / ges))
ff_i = anteil(ist, "fluorfrei")
fh_i = anteil(ist, "fluorhaltig")
print("Ist inkl. Notfall (24.000 l fluorhaltig): fluorfrei-Anteil {:.1f} %".format(
    100 * ff_i / (Li + 24000)))
# Plan-Durchschnitt je Linie
for linie in ("fluorfrei", "fluorhaltig", "offen"):
    u = sum(z["u"] for k, z in plan.items() if k[0] == linie)
    d = sum(z["db"] for k, z in plan.items() if k[0] == linie)
    l = sum(z["l"] for k, z in plan.items() if k[0] == linie)
    print("Plan {}: Ø Umsatz/l {:.2f}, Ø DB/l {:.2f}, DB-Marge {:.1f} %".format(linie, u / l, d / l, 100 * d / u))
