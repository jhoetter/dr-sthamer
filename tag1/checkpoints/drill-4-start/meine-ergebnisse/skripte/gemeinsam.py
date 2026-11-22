# -*- coding: utf-8 -*-
"""Gemeinsame Bereinigung der Auftragsdaten für alle Dashboard-Reiter (nur Standardbibliothek).

Regeln aus daten/kennzahlen.json:
- Doppelimporte: gleiche auftrag_id + position nur einmal zählen
- Liter: menge_l, fehlt es: menge x Gebindegröße (IBC 1.000, Fass 200, Kanister 20, l 1)
- Jahr nach Lieferdatum; Muster zählen nicht zum Absatz und haben 0 EUR
- Nettoumsatz: nettobetrag in EUR zum Konzernkurs des Lieferjahres (2027 = Kurs 2026)
"""
import csv
import json
import os
from datetime import date

BASIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATEN = os.path.join(BASIS, "daten")
STICHTAG = date(2027, 2, 28)
FENSTER_24M_AB = date(2025, 3, 1)
GEBINDE = {"IBC": 1000, "Fass": 200, "Kanister": 20, "l": 1}


def lies(name):
    with open(os.path.join(DATEN, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def kennzahlen():
    with open(os.path.join(DATEN, "kennzahlen.json"), encoding="utf-8") as f:
        return json.load(f)


def kurse():
    return kennzahlen()["konzernkurse"]["kurse"]


def datum(s):
    return date(int(s[0:4]), int(s[5:7]), int(s[8:10]))


def positionen():
    """Bereinigte Positionen (ohne Doppelimporte) mit Liter und EUR. Gibt (liste, statistik) zurück."""
    k = kurse()
    gesehen = {}
    stat = {"zeilen": 0, "doppelt": 0, "doppelt_abweichend": 0, "menge_l_fehlt": 0, "muster": 0}
    out = []
    for z in lies("auftraege.csv"):
        stat["zeilen"] += 1
        schl = (z["auftrag_id"], z["position"])
        if schl in gesehen:
            stat["doppelt"] += 1
            if gesehen[schl] != z:
                stat["doppelt_abweichend"] += 1
            continue
        gesehen[schl] = z
        menge = float(z["menge"])
        if z["menge_l"].strip() != "":
            liter = float(z["menge_l"])
        else:
            stat["menge_l_fehlt"] += 1
            liter = menge * GEBINDE[z["einheit"]]
        ld = datum(z["lieferdatum"])
        jahr = ld.year
        betrag = float(z["nettobetrag"])
        kurs = 1.0 if z["waehrung"] == "EUR" else k[str(jahr)][z["waehrung"]]
        eur = betrag * kurs
        muster = (z["art"] == "Muster") or (z["auftragsart"] == "Muster")
        if muster:
            stat["muster"] += 1
        out.append({
            "auftrag_id": z["auftrag_id"], "position": z["position"], "ld": ld, "jahr": jahr,
            "kunde": z["kunde_id"], "ls": z["lieferstelle_id"], "produkt": z["produkt_id"],
            "anwendung": z["anwendung"], "vw": z["vertriebsweg"], "art_auftrag": z["auftragsart"],
            "art": z["art"], "liter": liter, "eur": eur, "betrag": betrag, "waehrung": z["waehrung"],
            "muster": muster, "quelle": z["quellsystem"], "einheit": z["einheit"], "menge": menge,
        })
    return out, stat


def kunden():
    return {z["id"]: z for z in lies("kunden.csv")}


def lieferstellen():
    return {z["lieferstelle_id"]: z for z in lies("lieferstellen.csv")}


def de(zahl, nachkomma=0):
    """Deutsche Zahlenschreibweise 1.234,5"""
    s = "{:,.{n}f}".format(zahl, n=nachkomma)
    return s.replace(",", "X").replace(".", ",").replace("X", ".")
