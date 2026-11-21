# Etappe 1: Tabellenüberblick und fünf Kennzahlen am Stichtag
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, lade_positionen, absatz, KZ

for name in ["kunden", "produkte", "lieferstellen", "auftraege", "preisliste_2025", "preisliste_2026",
             "herstellkosten", "fracht", "budget_2026", "kurse", "reklamationen", "kontakte"]:
    print(name, len(lese_csv(name + ".csv")))

pos, stat = lade_positionen()
print("Statistik Aufträge:", stat)
print("Positionen nach Bereinigung:", len(pos))

kunden = lese_csv("kunden.csv")
ls = lese_csv("lieferstellen.csv")
print("Kunden Stamm:", len(kunden), " Lieferstellen:", len(ls))

# Kennzahl: aktive Kunden nach Definition (Lieferung ab 01.03.2025)
akt = set(p["kunde_id"] for p in pos if p["art"] == "Lieferung" and p["datum"] >= "2025-03-01")
print("aktive Kunden nach Definition:", len(akt))

# 2026 Absatz, Umsatz, Fluorfrei
a26 = [p for p in pos if p["jahr"] == 2026 and absatz(p)]
liter = sum(p["liter"] for p in a26)
ff = sum(p["liter"] for p in a26 if p["linie"] == "fluorfrei")
umsatz = sum(p["umsatz_eur"] for p in a26)
print("Absatz 2026 Liter:", liter)
print("Fluorfrei Liter 2026:", ff, "Anteil:", ff / liter)
print("Nettoumsatz 2026 EUR:", umsatz)
print("Positionen 2026 (ohne Muster):", len(a26))
print("Linien 2026 Liter:", {l: sum(p["liter"] for p in a26 if p["linie"] == l) for l in ("fluorhaltig", "fluorfrei", "offen")})

# Abweichung Deklaration vs Produktlinie
prod = lese_csv("produkte.csv")
for r in prod:
    if (r["produktlinie"] == "fluorfrei") != (r["fluorfrei_deklariert"] == "ja"):
        print("Abweichung Deklaration:", r["id"], r["name"], r["produktlinie"], r["fluorfrei_deklariert"])
