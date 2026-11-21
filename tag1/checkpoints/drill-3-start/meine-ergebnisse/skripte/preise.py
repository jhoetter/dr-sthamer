# Rabattquote und Listenpreis gegen realisierten Preis nach kennzahlen.json -> definitionen.rabattquote
# Rabattquote = 1 - Summe Nettobetrag (EUR, Konzernkurs) / Summe Listenwert; Listenwert = Menge x Listenpreis desselben Gebindes
# der Preisliste des Lieferjahres; nur Lieferungen, ohne Notfallservice, ohne Doppelimporte; nur 2025 und 2026.
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv


def preislisten():
    pl = {}
    for jahr in (2025, 2026):
        for r in lese_csv("preisliste_{}.csv".format(jahr)):
            pl[(jahr, r["produkt_id"], r["gebinde"])] = float(r["preis_netto_eur"])
    return pl


def rabatt_gruppen(pos, schluessel):
    """Summen je Gruppe: Positionen, Liter, Nettobetrag, Listenwert; Positionen ohne Listenpreis werden gezählt."""
    pl = preislisten()
    g = defaultdict(lambda: {"n": 0, "liter": 0.0, "netto": 0.0, "liste": 0.0, "ohne_liste": 0})
    for p in pos:
        if p["jahr"] not in (2025, 2026) or p["art"] != "Lieferung" or p["vertriebsweg"] == "Notfallservice":
            continue
        z = g[schluessel(p)]
        preis = pl.get((p["jahr"], p["produkt_id"], p["einheit"]))
        if preis is None:
            z["ohne_liste"] += 1
            continue
        z["n"] += 1
        z["liter"] += p["liter"]
        z["netto"] += p["umsatz"]
        z["liste"] += p["menge"] * preis
    for z in g.values():
        z["quote"] = (1 - z["netto"] / z["liste"]) if z["liste"] else None
        z["liste_je_l"] = z["liste"] / z["liter"] if z["liter"] else None
        z["real_je_l"] = z["netto"] / z["liter"] if z["liter"] else None
    return g


def listenpreiserhoehung_2026(pos):
    """Korb 2026: Listenwert mit Liste 2026 gegen Listenwert derselben Mengen mit Liste 2025."""
    pl = preislisten()
    a = b = 0.0
    fehlt = 0
    for p in pos:
        if p["jahr"] != 2026 or p["art"] != "Lieferung" or p["vertriebsweg"] == "Notfallservice":
            continue
        p25 = pl.get((2025, p["produkt_id"], p["einheit"]))
        p26 = pl.get((2026, p["produkt_id"], p["einheit"]))
        if p25 is None or p26 is None:
            fehlt += 1
            continue
        a += p["menge"] * p25
        b += p["menge"] * p26
    return a, b, fehlt
