# -*- coding: utf-8 -*-
"""Gemeinsame Finanzrechnung (Deckungsbeitrag) für Reiter „Finanzen“, Brücke und Kommentar.

Definitionen (daten/kennzahlen.json, definitionen.deckungsbeitrag):
- Nettoumsatz: Summe Nettobetrag aller Positionen (Gutschriften/Retouren negativ, Muster 0), EUR,
  ohne Doppelimporte, Jahr nach Lieferdatum. Fremdwährung: Konzernkurs des Lieferjahres ("konzern")
  oder Ist-Monatskurs des Liefermonats ("monat", nur 2026, für den Plan-Ist-Vergleich).
- Herstellkosten: Liter x (Rohstoff + Fertigung) je Produkt und Lieferjahr; Lieferungen und Muster zählen,
  Retouren mindern (negative Liter), Gutschriften ohne Herstellkosten.
- Fracht: je Auftrag aus fracht.csv, nach Litern auf die Positionen (Lieferung/Muster) des Auftrags verteilt,
  Jahr nach Lieferdatum der Position.
- Produktgruppe = Schaumart aus produkte.csv.
"""
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gemeinsam as g


def lade():
    pos, stat = g.positionen()
    kd = g.kunden()
    prod = {z["id"]: z for z in g.lies("produkte.csv")}
    hk = {}
    for z in g.lies("herstellkosten.csv"):
        hk[(z["produkt_id"], int(z["jahr"]))] = float(z["rohstoff_eur_l"]) + float(z["fertigung_eur_l"])
    fracht = {}
    fracht_doppelt = 0
    for z in g.lies("fracht.csv"):
        if z["auftrag_id"] in fracht:
            fracht_doppelt += 1
        fracht[z["auftrag_id"]] = (float(z["frachtkosten_eur"]), float(z["liter"]))
    kurs_monat = {}
    plan_kurs = {}
    for z in g.lies("kurse.csv"):
        kurs_monat[(z["monat"], z["waehrung"])] = float(z["ist_kurs_eur"])
        plan_kurs[(z["monat"], z["waehrung"])] = float(z["plankurs_eur"])

    # Fracht-Schlüssel: Liter der Lieferungen/Muster je Auftrag
    liter_auftrag = defaultdict(float)
    for p in pos:
        if p["art"] in ("Lieferung", "Muster"):
            liter_auftrag[p["auftrag_id"]] += p["liter"]

    pruef = {"fracht_liter_abweichend": 0, "auftraege_mit_fracht": len(fracht), "fracht_ohne_auftrag": 0,
             "positionen_ohne_hk": 0, "fracht_doppelt": fracht_doppelt, "fracht_summe_tabelle": sum(v[0] for v in fracht.values())}
    for a, (f, l) in fracht.items():
        if a not in liter_auftrag:
            pruef["fracht_ohne_auftrag"] += 1
        elif abs(liter_auftrag[a] - l) > 0.5:
            pruef["fracht_liter_abweichend"] += 1

    for p in pos:
        p["schaumart"] = prod[p["produkt"]]["schaumart"]
        p["segment"] = kd[p["kunde"]]["segment"]
        p["monat"] = p["ld"].strftime("%Y-%m")
        # Herstellkosten
        if p["art"] in ("Lieferung", "Muster", "Retoure"):
            satz = hk.get((p["produkt"], p["jahr"]))
            if satz is None:
                pruef["positionen_ohne_hk"] += 1
                satz = 0.0
            p["hk"] = p["liter"] * satz   # Retoure: Liter negativ -> mindert
        else:
            p["hk"] = 0.0                  # Gutschrift: Ware bleibt beim Kunden
        # Fracht
        if p["art"] in ("Lieferung", "Muster") and p["auftrag_id"] in fracht and liter_auftrag[p["auftrag_id"]]:
            p["fracht"] = fracht[p["auftrag_id"]][0] * p["liter"] / liter_auftrag[p["auftrag_id"]]
        else:
            p["fracht"] = 0.0
        # Umsatz zum Monatskurs (nur 2026 sinnvoll) und zum Plankurs
        if p["waehrung"] == "EUR":
            p["eur_monat"] = p["betrag"]
            p["eur_plan"] = p["betrag"]
            p["fx_effekt"] = 0.0
        elif p["jahr"] == 2026:
            kmo = kurs_monat[(p["monat"], p["waehrung"])]
            kpl = plan_kurs[(p["monat"], p["waehrung"])]
            p["eur_monat"] = p["betrag"] * kmo
            p["eur_plan"] = p["betrag"] * kpl
            p["fx_effekt"] = p["betrag"] * (kmo - kpl)
        else:
            p["eur_monat"] = p["eur"]
            p["eur_plan"] = p["eur"]
            p["fx_effekt"] = 0.0
    return pos, kd, prod, pruef


def summiere(pos, schluessel, jahr, filt=None, umsatz="eur"):
    """Gruppensummen: Nettoumsatz, Herstellkosten, Fracht, DB, Positionen, Liter (Absatz ohne Muster)."""
    r = defaultdict(lambda: {"umsatz": 0.0, "hk": 0.0, "fracht": 0.0, "n": 0, "liter": 0.0})
    for p in pos:
        if p["jahr"] != jahr or (filt and not filt(p)):
            continue
        w = r[schluessel(p)]
        w["umsatz"] += p[umsatz]
        w["hk"] += p["hk"]
        w["fracht"] += p["fracht"]
        w["n"] += 1
        if not p["muster"]:
            w["liter"] += p["liter"]
    for w in r.values():
        w["db"] = w["umsatz"] - w["hk"] - w["fracht"]
        w["marge"] = w["db"] / w["umsatz"] if w["umsatz"] else None
    return r


def eur(x, n=0):
    return g.de(x, n)
