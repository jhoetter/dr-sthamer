# Gemeinsame Funktionen für die Auswertungen von Tag 1 (nur Standardbibliothek)
import csv
import json
import os

BASIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
DATEN = os.path.join(BASIS, "daten")


def lese_csv(name):
    with open(os.path.join(DATEN, name), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def lese_kennzahlen():
    with open(os.path.join(DATEN, "kennzahlen.json"), encoding="utf-8") as f:
        return json.load(f)


KZ = lese_kennzahlen()
GEBINDE = KZ["definitionen"]["umrechnung_gebinde"]
KURSE = KZ["konzernkurse"]["kurse"]


def lade_positionen():
    """Auftragspositionen, bereinigt: Doppelimporte einmal, Muster getrennt markiert.

    Gibt (positionen, statistik) zurück. Jede Position hat: jahr, liter (netto, mit
    Vorzeichen), umsatz_eur (Konzernkurs des Lieferjahres), linie, segment, land, ...
    """
    kunden = {r["id"]: r for r in lese_csv("kunden.csv")}
    produkte = {r["id"]: r for r in lese_csv("produkte.csv")}
    gesehen = set()
    pos = []
    stat = {"zeilen": 0, "doppelt": 0, "muster": 0, "gutschrift": 0, "retoure": 0,
            "liter_umgerechnet": 0}
    for r in lese_csv("auftraege.csv"):
        stat["zeilen"] += 1
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
        if art == "Muster":
            stat["muster"] += 1
        elif art == "Gutschrift":
            stat["gutschrift"] += 1
        elif art == "Retoure":
            stat["retoure"] += 1
        jahr = int(r["lieferdatum"][:4])
        kurs = 1.0 if r["waehrung"] == "EUR" else KURSE[str(jahr)][r["waehrung"]]
        umsatz = float(r["nettobetrag"]) * kurs
        k = kunden[r["kunde_id"]]
        p = produkte[r["produkt_id"]]
        pos.append({
            "auftrag_id": r["auftrag_id"], "position": r["position"],
            "datum": r["lieferdatum"], "jahr": jahr,
            "kunde_id": r["kunde_id"], "segment": k["segment"], "land": k["land"],
            "lieferstelle_id": r["lieferstelle_id"], "produkt_id": r["produkt_id"],
            "linie": p["produktlinie"], "anwendung": r["anwendung"],
            "vertriebsweg": r["vertriebsweg"], "art": art,
            "liter": liter, "umsatz_eur": umsatz, "waehrung": r["waehrung"],
        })
    return pos, stat


def absatz(p):
    """Zählt zum Absatz (ohne Muster)."""
    return p["art"] != "Muster"
