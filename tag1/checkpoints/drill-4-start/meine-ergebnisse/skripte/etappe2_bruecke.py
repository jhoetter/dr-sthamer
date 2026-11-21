# Etappe 2 Drill 2: Brücken Budget -> Ist 2026 (Umsatz und Deckungsbeitrag) mit Abgleich
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fin_kern import lade_fin, summiere
from bruecke import bruecke, fx_je_waehrung


def f(x):
    return "{:,.2f}".format(x).replace(",", "X").replace(".", ",").replace("X", ".")


pos, stat = lade_fin()
for wert, name in (("u", "NETTOUMSATZ"), ("db", "DECKUNGSBEITRAG (nach Herstellkosten und Fracht)")):
    b = bruecke(pos, wert)
    print("=== Brücke", name, "2026, EUR ===")
    print("Budget (Plankurs):                  ", f(b["plan"]))
    print("Liter: Plan {:,.0f}  Ist ohne Notfall {:,.0f}  Plan-Durchschnitt je Liter {:.4f}".format(
        b["L_plan"], b["L_ist"], b["avg_plan"]))
    for k, t in (("menge", "Mengeneffekt"), ("mix", "Mixeffekt"), ("preis", "Preiseffekt"),
                 ("kosten", "Kosteneffekt"), ("fx", "Fremdwährungseffekt"), ("notfall", "Notfallservice (nicht budgetiert)")):
        if wert == "u" and k == "kosten":
            continue
        print("{:<36}{:>16}".format(t, f(b[k])))
    print("Ist (Ist-Monatskurse, inkl. Notfall):", f(b["ist"]), " davon Zellen ohne Notfall:", f(b["ist_zellen"]))
    print("Gesamtabweichung Ist - Budget:      ", f(b["gesamtabweichung"]))
    print("Summe der Effekte:                  ", f(b["summe_effekte"]))
    print("Differenz (muss 0,00 sein):         ", f(b["differenz"]))
    print()

print("=== Fremdwährungseffekt 2026 je Währung (Umsatz, ohne Notfall) ===")
g = fx_je_waehrung(pos)
tot = 0.0
for w in sorted(g):
    z = g[w]
    tot += z["effekt"]
    print(w, z["n"], "Pos.", "Betrag in FW", f(z["betrag_fw"]), "Effekt EUR", f(z["effekt"]))
print("Summe", f(tot))
print()
# Bezug zum Konzernkurs
k = summiere(pos, lambda p: "x", lambda p: p["jahr"] == 2026)["x"]
print("Zum Vergleich (Konzernkurs 2026, inkl. Notfall): Umsatz {} DB {}".format(f(k["umsatz"]), f(k["db"])))
