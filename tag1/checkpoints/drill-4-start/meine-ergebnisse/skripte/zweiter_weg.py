import csv
import json
import os
from collections import defaultdict

JAHR = "2026"
GEBINDE = {"IBC": 1000.0, "Fass": 200.0, "Kanister": 20.0, "l": 1.0}

HIER = os.path.dirname(os.path.abspath(__file__))
DATEN = os.path.normpath(os.path.join(HIER, "..", "..", "daten"))


def lies(name):
    pfad = os.path.join(DATEN, name)
    with open(pfad, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def zahl(text):
    text = (text or "").strip()
    if text == "":
        return None
    return float(text)


def literzahl(zeile):
    menge = zahl(zeile["menge"])
    menge_l = zahl(zeile["menge_l"])
    if menge_l is None:
        menge_l = menge * GEBINDE[zeile["einheit"].strip()]
    return menge_l


# Stammdaten
with open(os.path.join(DATEN, "kennzahlen.json"), encoding="utf-8-sig") as f:
    kennzahlen = json.load(f)
konzernkurs = dict(kennzahlen["konzernkurse"]["kurse"][JAHR])
konzernkurs["EUR"] = 1.0

istkurs = {}
for z in lies("kurse.csv"):
    istkurs[(z["monat"].strip(), z["waehrung"].strip())] = float(z["ist_kurs_eur"])

herstell = {}
for z in lies("herstellkosten.csv"):
    herstell[(z["produkt_id"].strip(), z["jahr"].strip())] = (
        float(z["rohstoff_eur_l"]) + float(z["fertigung_eur_l"])
    )

fracht_auftrag = {}
for z in lies("fracht.csv"):
    fracht_auftrag[z["auftrag_id"].strip()] = fracht_auftrag.get(
        z["auftrag_id"].strip(), 0.0
    ) + float(z["frachtkosten_eur"])

# (a) Budget
budget_db = 0.0
budget_umsatz = 0.0
for z in lies("budget_2026.csv"):
    budget_db += float(z["db_eur"])
    budget_umsatz += float(z["umsatz_eur"])

# Positionen einlesen, Doppelimporte einmal zaehlen
gesehen = set()
positionen = []
for z in lies("auftraege.csv"):
    schluessel = (z["auftrag_id"].strip(), z["position"].strip())
    if schluessel in gesehen:
        continue
    gesehen.add(schluessel)
    z["_liter"] = literzahl(z)
    positionen.append(z)

# Fracht je Auftrag: Gewichte = Liter der Lieferungen/Muster (nur diese tragen Fracht)
gewicht = defaultdict(float)
for z in positionen:
    if z["art"].strip() in ("Lieferung", "Muster"):
        gewicht[z["auftrag_id"].strip()] += abs(z["_liter"])


def rechne(modus, ohne_notfall=False, nur_notfall=False):
    liter = umsatz = kosten = fracht = 0.0
    for z in positionen:
        if not z["lieferdatum"].strip().startswith(JAHR):
            continue
        notfall = z["vertriebsweg"].strip() == "Notfallservice"
        if ohne_notfall and notfall:
            continue
        if nur_notfall and not notfall:
            continue
        art = z["art"].strip()
        wk = z["waehrung"].strip()
        monat = z["lieferdatum"].strip()[:7]
        if modus == "konzern":
            kurs = konzernkurs[wk]
        else:
            kurs = 1.0 if wk == "EUR" else istkurs[(monat, wk)]
        l = z["_liter"]
        liter += l
        if art != "Muster":
            umsatz += zahl(z["nettobetrag"]) * kurs
        if art in ("Lieferung", "Muster", "Retoure"):
            kosten += l * herstell[(z["produkt_id"].strip(), z["lieferdatum"].strip()[:4])]
        if art in ("Lieferung", "Muster"):
            aid = z["auftrag_id"].strip()
            if aid in fracht_auftrag and gewicht[aid] > 0:
                fracht += fracht_auftrag[aid] * abs(l) / gewicht[aid]
    return liter, umsatz, kosten, fracht, umsatz - kosten - fracht


def f(x):
    return "{:,.2f}".format(x)


print("(a) Budget 2026")
print("  Budget-Deckungsbeitrag EUR:", f(budget_db))
print("  Budget-Nettoumsatz EUR:   ", f(budget_umsatz))

for titel, modus in (("(b1) Ist mit Konzernkurs 2026", "konzern"), ("(b2) Ist mit Ist-Monatskurs", "monat")):
    li, um, ko, fr, db = rechne(modus)
    print(titel)
    print("  Liter:", f(li), " Nettoumsatz:", f(um), " Herstellkosten:", f(ko), " Fracht:", f(fr), " DB:", f(db))

li, um, ko, fr, db = rechne("monat", nur_notfall=True)
print("(c) Notfallservice 2026 (Ist-Monatskurs)")
print("  Liter:", f(li), " Nettoumsatz:", f(um), " Herstellkosten:", f(ko), " Fracht:", f(fr), " DB:", f(db))

li, um, ko, fr, db = rechne("monat", ohne_notfall=True)
print("(d) Ist ohne Notfallservice (Ist-Monatskurs)")
print("  Liter:", f(li), " Nettoumsatz:", f(um), " Herstellkosten:", f(ko), " Fracht:", f(fr), " DB:", f(db))
