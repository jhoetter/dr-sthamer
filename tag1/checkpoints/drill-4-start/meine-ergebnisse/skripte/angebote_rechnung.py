# -*- coding: utf-8 -*-
"""Rechnet die Preise der Vorgänge A-01 und A-02 nach RL-ANG-2026 nach.
Liest nur daten/ (Preislisten, Herstellkosten, Aufträge). Schreibt nichts, gibt nur aus."""
import csv
import os
from decimal import Decimal, ROUND_HALF_UP

BASIS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
D = lambda *p: os.path.join(BASIS, "daten", *p)


def cent(x):
    return Decimal(x).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def preisliste(jahr):
    p = {}
    with open(D("preisliste_%d.csv" % jahr), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            p[(r["produkt_id"], r["gebinde"])] = Decimal(r["preis_netto_eur"])
    return p


def herstellkosten(produkt, jahr):
    with open(D("herstellkosten.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["produkt_id"] == produkt and int(r["jahr"]) == jahr:
                return Decimal(r["rohstoff_eur_l"]) + Decimal(r["fertigung_eur_l"])
    return None


def position(preis, anzahl, satz):
    """Positionspreis = Listenwert x (1 - Summe der Rabattsätze), auf Cent (§ 3 Nr. 5)."""
    liste = preis * anzahl
    return liste, cent(liste * (Decimal(1) - satz))


def a01():
    print("=== A-01 ===")
    pl25, pl26 = preisliste(2025), preisliste(2026)
    # 800 + 800 Befüllung (1 IBC + 3 Fass je 1.600 l zusammen), 600 Reserve (3 Fass)
    pos = [("IBC", 1, True), ("Fass", 3, True), ("Fass", 3, False)]  # Gebinde, Anzahl, Befüllung?
    # Assistent: Preisliste 2025, 13 % auf alles
    s_liste, s_netto = Decimal(0), Decimal(0)
    for g, n, bef in pos:
        l, nn = position(pl25[("P-104", g)], n, Decimal("0.13"))
        s_liste += l
        s_netto += nn
    print("Assistent (PL 2025, 13 % auf alles): Liste", s_liste, "netto", s_netto)
    # richtig nach Richtlinie: Mengenrabatt 3 % auf alles (2.200 l, Stufe ab 1.000 l), Projekt 5 % nur Befüllung
    for name, pl in (("PL 2025", pl25), ("PL 2026", pl26)):
        liste, netto = Decimal(0), Decimal(0)
        zeilen = []
        for g, n, bef in pos:
            satz = Decimal("0.03") + (Decimal("0.05") if bef else Decimal(0))
            l, nn = position(pl[("P-104", g)], n, satz)
            liste += l
            netto += nn
            zeilen.append((g, n, bef, pl[("P-104", g)], l, satz, nn))
        print("Richtlinie,", name, ": Liste", liste, "netto", netto)
        for z in zeilen:
            print("   ", z)
    # Kundenstatus: letzte Lieferung (ohne Muster) von K-1018
    letzte = None
    n24_neu, n24_alt = 0, 0
    with open(D("auftraege.csv"), encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            if r["kunde_id"] != "K-1018" or r["art"] != "Lieferung" or r["auftragsart"] == "Muster":
                continue
            d = r["lieferdatum"]
            if letzte is None or d > letzte:
                letzte = d
            if "2025-03-01" <= d <= "2027-03-01":
                n24_neu += 1
            if "2024-07-14" <= d <= "2026-07-14":
                n24_alt += 1
    print("K-1018 letzte Lieferung:", letzte, "| Lieferungen 24 Monate vor 01.03.2027:", n24_neu,
          "| vor 14.07.2026:", n24_alt)


def a02():
    print("=== A-02 ===")
    pl26 = preisliste(2026)
    ibc, kan = pl26[("P-111", "IBC")], pl26[("P-111", "Kanister")]
    jahr_liste = 9 * ibc + 150 * kan
    print("Liste je Vertragsjahr: 9 IBC", 9 * ibc, "+ 150 Kanister", 150 * kan, "=", jahr_liste,
          "| 3 Jahre:", 3 * jahr_liste, "| je Liter:", cent(jahr_liste / 12000))
    hk = herstellkosten("P-111", 2027)
    print("Herstellkosten P-111 2027 je Liter:", hk, "| je Vertragsjahr (12.000 l):", hk * 12000)
    for satz in ("0", "0.04", "0.05", "0.06", "0.08", "0.18"):
        s = Decimal(satz)
        umsatz_j = cent(jahr_liste * (1 - s))
        umsatz_3 = cent(3 * jahr_liste * (1 - s))
        db = umsatz_j - hk * 12000
        print("Rabatt %5s %%: Auftragswert 3 Jahre %s | je Jahr %s | DB vor Fracht je Jahr %s | DB-Marge vor Fracht %.1f %%"
              % (s * 100, umsatz_3, umsatz_j, cent(db), db / umsatz_j * 100))
    # Rabatt, bei dem der Auftragswert unter 150.000 läge
    print("Rabatt für Auftragswert 150.000:", (1 - Decimal(150000) / (3 * jahr_liste)) * 100)


if __name__ == "__main__":
    a01()
    a02()
