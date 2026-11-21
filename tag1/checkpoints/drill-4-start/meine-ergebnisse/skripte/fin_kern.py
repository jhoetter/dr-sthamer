# Gemeinsame Finanzfunktionen (Drill 2), nur Standardbibliothek
# Definitionen: daten/kennzahlen.json -> definitionen.deckungsbeitrag, umrechnung_fremdwaehrung, plan_ist_bruecke
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from kern import lese_csv, KZ, GEBINDE, KURSE


def lade_fin():
    """Positionen mit Umsatz, Herstellkosten und Fracht.

    Umsatz: nettobetrag in EUR zum Konzernkurs des Lieferjahres (konz) und zum Ist-Monatskurs
    2026 (ist_m, nur 2026) sowie zum Plankurs (plan, nur 2026).
    Herstellkosten: Liter x Kosten/l (Produkt, Lieferjahr). Lieferung, Muster: +; Retoure: negative Liter
    mindern; Gutschrift: 0.
    Fracht: je Auftrag nach Litern auf Lieferungen/Muster des Auftrags verteilt.
    """
    kunden = {r["id"]: r for r in lese_csv("kunden.csv")}
    produkte = {r["id"]: r for r in lese_csv("produkte.csv")}
    hk = {}
    for r in lese_csv("herstellkosten.csv"):
        hk[(r["produkt_id"], int(r["jahr"]))] = float(r["rohstoff_eur_l"]) + float(r["fertigung_eur_l"])
    fracht = {r["auftrag_id"]: float(r["frachtkosten_eur"]) for r in lese_csv("fracht.csv")}
    fracht_l = {r["auftrag_id"]: float(r["liter"]) for r in lese_csv("fracht.csv")}
    kurs_ist = {}
    kurs_plan = {}
    for r in lese_csv("kurse.csv"):
        kurs_ist[(r["monat"], r["waehrung"])] = float(r["ist_kurs_eur"])
        kurs_plan[r["waehrung"]] = float(r["plankurs_eur"])

    gesehen = set()
    pos = []
    stat = defaultdict(int)
    for r in lese_csv("auftraege.csv"):
        schluessel = (r["auftrag_id"], r["position"])
        if schluessel in gesehen:
            stat["doppelt"] += 1
            continue
        gesehen.add(schluessel)
        if r["menge_l"].strip() == "":
            liter = float(r["menge"]) * GEBINDE[r["einheit"]]
            stat["liter_umgerechnet"] += 1
        else:
            liter = float(r["menge_l"])
        art = r["art"]
        stat[art] += 1
        jahr = int(r["lieferdatum"][:4])
        monat = r["lieferdatum"][:7]
        w = r["waehrung"]
        betrag = float(r["nettobetrag"])
        konz = betrag if w == "EUR" else betrag * KURSE[str(jahr)][w]
        ist_m = betrag if w == "EUR" else (betrag * kurs_ist[(monat, w)] if jahr == 2026 else None)
        plan = betrag if w == "EUR" else (betrag * kurs_plan[w] if jahr == 2026 else None)
        k = kunden[r["kunde_id"]]
        p = produkte[r["produkt_id"]]
        if art == "Gutschrift":
            herst = 0.0
        else:
            herst = liter * hk[(r["produkt_id"], jahr)]
        pos.append({
            "auftrag_id": r["auftrag_id"], "position": r["position"], "datum": r["lieferdatum"],
            "monat": monat, "jahr": jahr, "kunde_id": r["kunde_id"], "segment": k["segment"],
            "produkt_id": r["produkt_id"], "linie": p["produktlinie"], "art": art,
            "vertriebsweg": r["vertriebsweg"], "liter": liter, "waehrung": w,
            "betrag_fw": betrag, "umsatz": konz, "umsatz_ist_m": ist_m, "umsatz_plan": plan,
            "herst": herst, "fracht": 0.0, "einheit": r["einheit"], "menge": float(r["menge"]),
            "preis_einheit": float(r["preis_netto_je_einheit"]),
        })
    # Fracht verteilen: Liter der Lieferungen/Muster je Auftrag
    summe_l = defaultdict(float)
    for p in pos:
        if p["art"] in ("Lieferung", "Muster"):
            summe_l[p["auftrag_id"]] += p["liter"]
    stat["fracht_auftraege"] = len(fracht)
    ohne = 0
    for p in pos:
        if p["art"] in ("Lieferung", "Muster"):
            a = p["auftrag_id"]
            if a in fracht and summe_l[a] > 0:
                p["fracht"] = fracht[a] * p["liter"] / summe_l[a]
            else:
                ohne += 1
    stat["lieferpositionen_ohne_fracht"] = ohne
    # Abgleich: verteilte Fracht = Tabelle
    stat["fracht_summe_tabelle"] = round(sum(fracht.values()), 2)
    stat["fracht_summe_verteilt"] = round(sum(p["fracht"] for p in pos), 2)
    return pos, stat


def absatz(p):
    return p["art"] != "Muster"


def summiere(pos, schluessel, filt=None):
    """Summen je Gruppe; Marge nie gemittelt, immer aus den Summen."""
    g = defaultdict(lambda: {"n": 0, "liter": 0.0, "umsatz": 0.0, "herst": 0.0, "fracht": 0.0})
    for p in pos:
        if filt and not filt(p):
            continue
        z = g[schluessel(p)]
        z["n"] += 1
        # Liter im Absatz: ohne Muster; Muster tragen nur Kosten
        if absatz(p):
            z["liter"] += p["liter"]
        z["umsatz"] += p["umsatz"]
        z["herst"] += p["herst"]
        z["fracht"] += p["fracht"]
    for z in g.values():
        z["db"] = z["umsatz"] - z["herst"] - z["fracht"]
        z["marge"] = (z["db"] / z["umsatz"]) if z["umsatz"] else None
    return g
