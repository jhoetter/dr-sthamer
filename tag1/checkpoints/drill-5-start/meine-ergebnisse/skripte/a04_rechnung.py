# -*- coding: utf-8 -*-
"""Rechnet Vorgang A-04 (K-1020, Nachbestellung P-106) nach RL-ANG-2026 nach.
Liest nur daten/. Schreibt nichts, gibt nur aus."""
import csv
import os
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP

BASIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
D = lambda *p: os.path.join(BASIS, "daten", *p)
cent = lambda x: Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

ANGEBOTSDATUM = date(2027, 3, 1)
LITER = {"IBC": 1000, "Fass": 200, "Kanister": 20}
BESTELLUNG = [("IBC", 7), ("Fass", 1), ("Kanister", 8)]

pl = {}
with open(D("preisliste_2026.csv"), encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        pl[(r["produkt_id"], r["gebinde"])] = Decimal(r["preis_netto_eur"])

menge = sum(LITER[g] * n for g, n in BESTELLUNG)
satz = Decimal("0.00")
for grenze, s in ((1000, "0.03"), (5000, "0.06"), (20000, "0.10")):
    if menge >= grenze:
        satz = Decimal(s)
print("Gesamtmenge P-106: %d l -> Mengenrabatt %s %%" % (menge, satz * 100))

gesamt = Decimal(0)
liste_ges = Decimal(0)
for g, n in BESTELLUNG:
    liste = pl[("P-106", g)] * n
    netto = cent(liste * (1 - satz))
    liste_ges += liste
    gesamt += netto
    print("%2d x %-8s Liste je Gebinde %9s  Listenwert %10s  netto %10s" % (n, g, pl[("P-106", g)], cent(liste), netto))
print("Listenwert gesamt %s, Auftragswert netto %s, Abstand zu 25.000: %s" % (cent(liste_ges), gesamt, cent(25000 - gesamt)))
print("Ohne Mengenrabatt: %s (über 25.000: %s)" % (cent(liste_ges), liste_ges > 25000))
print("Frei Haus ab 2.500: %s; Expresszuschlag 450,00 zählt nicht zum Auftragswert" % (gesamt >= 2500))

# Kundenstatus
letzte = None
with open(D("auftraege.csv"), encoding="utf-8-sig", newline="") as f:
    for r in csv.DictReader(f):
        if r["kunde_id"] == "K-1020" and r["art"] == "Lieferung":
            d = date.fromisoformat(r["lieferdatum"])
            if letzte is None or d > letzte:
                letzte = d
print("Letzte Lieferung (ohne Muster): %s -> Bestandskunde: %s" % (letzte, letzte >= date(2025, 3, 1)))

# Fristen
print("Gültig bis (60 Tage): %s" % (ANGEBOTSDATUM + timedelta(days=60)))
d, n = date(2027, 2, 24), 0
while n < 3:
    d += timedelta(days=1)
    if d.weekday() < 5:
        n += 1
print("Antwortfrist 3 Arbeitstage ab Eingang 24.02.2027: %s (%s)" % (d, d.strftime("%A")))
with open(D("herstellkosten.csv"), encoding="utf-8-sig", newline="") as f:
    pass
