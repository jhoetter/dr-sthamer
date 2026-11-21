#!/usr/bin/env python3
"""Erzeugt die Tabellen für Tag 1 «AI Augmentation» unter tag1/daten/.

Nur Standardbibliothek, Python >= 3.9, deterministisch ohne Zufallsgenerator:
Alle «zufälligen» Werte kommen aus _h(...), einem SHA-256 über feste Texte.

Liest aus ../data nur kunden.json, produkte.json und lieferungen.json.
Schreibt nur unter tag1/daten/.

Aufruf (im Ordner tag1/ oder von überall):
    python werkzeuge/erzeuge_daten.py                 schreibt die Dateien
    python werkzeuge/erzeuge_daten.py --check         vergleicht Byte für Byte und prüft die Regeln
    python werkzeuge/erzeuge_daten.py --sollwerte P   schreibt Sollwerte nach P (nur ausserhalb des Repos)
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sys
from datetime import date, timedelta
from pathlib import Path

sys.dont_write_bytecode = True

WERKZEUGE = Path(__file__).resolve().parent
TAG1 = WERKZEUGE.parent
REPO = TAG1.parent
QUELLE = REPO / "data"
ZIEL = TAG1 / "daten"

START = date(2021, 1, 1)
STICHTAG = date(2027, 2, 28)
HEUTE = date(2027, 3, 1)
ERP_WECHSEL = date(2024, 7, 1)
PORTAL_ASSISTENT_AB = date(2025, 10, 1)
RL_REKLAMATION_V11_AB = date(2026, 6, 16)
RUHEND_AB = date(2025, 10, 1)  # K-1029: keine Aufträge mehr ab Oktober 2025

GEBINDE_L = {"l": 1, "Kanister": 20, "Fass": 200, "IBC": 1000}

# --------------------------------------------------------------------------
# Hilfen
# --------------------------------------------------------------------------


def _h(*teile: object) -> int:
    """Stabile Pseudozufallszahl aus festen Texten (Präfix «tag1»)."""
    text = "|".join(["tag1"] + [str(t) for t in teile])
    return int(hashlib.sha256(text.encode("utf-8")).hexdigest()[:12], 16)


def _u(*teile: object) -> float:
    """Stabile Zahl in [0, 1)."""
    return (_h(*teile) % 1000003) / 1000003.0


def _d(text: str) -> date:
    return date.fromisoformat(text)


def _tage(von: date, bis: date, *teile: object) -> date:
    spanne = (bis - von).days
    return von + timedelta(days=_h(*teile) % (spanne + 1))


def _zahl(x: float, stellen: int = 2) -> str:
    """Dezimalpunkt, feste Stellen, ohne -0.00."""
    s = ("%." + str(stellen) + "f") % x
    if s.startswith("-") and float(s) == 0:
        s = s[1:]
    return s


def _ja(b: bool) -> str:
    return "ja" if b else "nein"


def lade_quelle() -> tuple[list, list, list]:
    kunden = json.loads((QUELLE / "kunden.json").read_text(encoding="utf-8"))
    produkte = json.loads((QUELLE / "produkte.json").read_text(encoding="utf-8"))
    lieferungen = json.loads((QUELLE / "lieferungen.json").read_text(encoding="utf-8"))
    return kunden, produkte, lieferungen


# --------------------------------------------------------------------------
# Feste Annahmen der Übungswelt
# --------------------------------------------------------------------------

# Einführungskalender (Johannes' Daten haben kein Einführungsdatum).
EINFUEHRUNG = {
    "P-101": "2009-04-01", "P-102": "2009-04-01", "P-103": "2011-09-01", "P-104": "2012-03-01",
    "P-105": "2013-05-01", "P-106": "2010-02-01", "P-107": "2014-06-01", "P-108": "2008-10-01",
    "P-113": "2012-01-15", "P-117": "2015-03-01", "P-120": "2016-02-01", "P-121": "2010-09-01",
    "P-110": "2012-05-01", "P-111": "2015-04-01", "P-112": "2019-03-01", "P-114": "2018-06-01",
    "P-115": "2019-02-01", "P-116": "2019-02-01", "P-118": "2020-04-01", "P-119": "2020-09-01",
    # fluorfreie Nachfolger, gestaffelt 2021-2025
    "P-201": "2021-03-01", "P-202": "2021-09-01", "P-206": "2022-03-01", "P-207": "2023-04-01",
    "P-204": "2023-10-01", "P-203": "2024-03-01", "P-205": "2025-02-01",
}

# Listenpreis 2026 je Liter in EUR (Gebindepreise werden daraus abgeleitet).
PREIS_L_2026 = {
    "P-101": 4.20, "P-102": 3.60, "P-103": 5.40, "P-104": 4.80, "P-105": 5.10, "P-106": 3.90,
    "P-107": 6.50, "P-108": 3.80, "P-113": 2.20, "P-117": 4.90, "P-120": 4.10, "P-121": 7.80,
    "P-110": 1.90, "P-111": 6.90, "P-112": 2.60, "P-114": 5.20, "P-115": 5.00, "P-116": 4.30,
    "P-118": 6.10, "P-119": 5.60, "P-201": 5.30, "P-202": 4.50, "P-203": 6.80, "P-204": 5.90,
    "P-205": 6.40, "P-206": 7.20, "P-207": 4.60,
}
# Lose Ware im Tankwagen (Preis je Liter) nur für Produkte stationärer Anlagen.
LOSE_WARE = {"P-103", "P-104", "P-105", "P-108", "P-117", "P-118", "P-119", "P-121",
             "P-203", "P-204", "P-205", "P-207"}
GEBINDE_FAKTOR = {"Kanister": 1.08, "Fass": 0.97, "IBC": 0.92, "l": 0.88}
PREISINDEX = {2021: 0.84, 2022: 0.88, 2023: 0.94, 2024: 0.97, 2025: 1 / 1.04, 2026: 1.0, 2027: 1.0}
# Preisdurchsetzung 2026 (siehe preisschutz_2026)
PREISSCHUTZ_HAENDLER = 0.975
PREISSCHUTZ_DIREKT_BIS = date(2026, 4, 1)

WAEHRUNG = {"K-1019": "NOK", "K-1021": "GBP", "K-1022": "CHF"}
# Konzernkurse: 1 Einheit Fremdwährung = x EUR (Jahresdurchschnitt, fiktiv gerundet)
KONZERNKURSE = {
    "2021": {"CHF": 0.925, "GBP": 1.163, "NOK": 0.0985},
    "2022": {"CHF": 0.995, "GBP": 1.173, "NOK": 0.0945},
    "2023": {"CHF": 1.029, "GBP": 1.150, "NOK": 0.0872},
    "2024": {"CHF": 1.052, "GBP": 1.181, "NOK": 0.0857},
    "2025": {"CHF": 1.066, "GBP": 1.187, "NOK": 0.0852},
    "2026": {"CHF": 1.071, "GBP": 1.168, "NOK": 0.0849},
    "2027": {"CHF": 1.071, "GBP": 1.168, "NOK": 0.0849},
}
RAHMENVERTRAG = {"K-1002", "K-1005", "K-1020"}

# Umsatz (Liter je Jahr als Vielfaches der Füllmenge) und Lieferungen je Jahr nach Anwendung.
UMSCHLAG = {"stationaere_anlage": 0.30, "feuerwehrfahrzeug": 0.85, "lager_bestand": 1.0,
            "uebung_training": 2.6, "tragbarer_feuerloescher": 1.3, "fahrbarer_feuerloescher": 0.9}
FREQUENZ = {"stationaere_anlage": 1.8, "feuerwehrfahrzeug": 3.0, "lager_bestand": 5.0,
            "uebung_training": 7.0, "tragbarer_feuerloescher": 10.0, "fahrbarer_feuerloescher": 6.0}

# Zeitliche Entwicklung (Faktor auf die Liter je Lieferung): fluorfreie Produkte wachsen,
# fluorhaltige werden ausser in stationären Anlagen weniger nachgekauft.
TREND_FLUORFREI = {2021: 2.0, 2022: 2.15, 2023: 2.3, 2024: 2.5, 2025: 2.75, 2026: 3.6, 2027: 3.6}
TREND_FLUORHALTIG = {2021: 1.15, 2022: 1.08, 2023: 1.0, 2024: 0.9, 2025: 0.78, 2026: 0.66, 2027: 0.66}
HAENDLER_FAKTOR = 2.0      # Händlerlager drehen schneller
FRUEHES_ENDE_FAKTOR = 0.6  # Lieferstellen ohne Lieferung seit 2026: seltener Bedarf

# Lieferzeilen mit fluorfreiem Produkt: Beginn der Belieferung oder Wechsel vom Vorgänger.
# ("start", Datum): Lieferstelle erst ab diesem Datum beliefert.
# ("wechsel", Datum, Vorgänger): vorher Vorgängerprodukt an derselben Lieferstelle.
# ("einmal", Art): genau eine Lieferung am Datum der letzten Lieferung (Erprobung/Muster).
VERLAUF = {
    # Übungsschaum: Wechsel TrainFoam Classic -> TrainFoam Fluorfrei
    "L-00006": ("wechsel", "2022-05-02", "P-113"), "L-00025": ("wechsel", "2023-03-06", "P-113"),
    "L-00041": ("wechsel", "2021-09-13", "P-113"), "L-00048": ("wechsel", "2022-10-04", "P-113"),
    "L-00054": ("wechsel", "2021-06-07", "P-113"), "L-00068": ("wechsel", "2024-02-05", "P-113"),
    "L-00074": ("wechsel", "2023-09-11", "P-113"), "L-00129": ("wechsel", "2024-06-03", "P-113"),
    "L-00132": ("wechsel", "2025-01-13", "P-113"),
    # Brandax Pro S -> Brandax Pro
    "L-00039": ("wechsel", "2022-04-04", "P-120"), "L-00040": ("wechsel", "2022-04-04", "P-120"),
    "L-00035": ("wechsel", "2023-05-08", "P-120"),
    # neue Fahrzeuge, Lager, Testanlagen
    "L-00044": ("start", "2022-06-01"), "L-00047": ("start", "2023-04-03"),
    "L-00061": ("start", "2021-03-01"), "L-00058": ("start", "2023-02-01"),
    "L-00110": ("start", "2021-05-03"), "L-00114": ("start", "2022-03-01"),
    "L-00108": ("start", "2022-01-10"), "L-00024": ("start", "2022-09-05"),
    "L-00038": ("start", "2024-03-04"), "L-00148": ("start", "2023-01-09"),
    "L-00015": ("start", "2024-02-05"), "L-00143": ("start", "2023-09-04"),
    "L-00147": ("start", "2024-05-06"), "L-00121": ("start", "2022-04-04"),
    "L-00123": ("start", "2023-03-01"), "L-00125": ("start", "2023-03-01"),
    # fluorfreie Nachfolger (FreeFoam)
    "L-00012": ("start", "2025-04-07"), "L-00028": ("start", "2023-06-05"),
    "L-00053": ("start", "2022-03-07"), "L-00073": ("start", "2025-03-03"),
    "L-00091": ("start", "2024-04-08"), "L-00115": ("start", "2021-10-04"),
    # Erprobungsmengen und Muster
    "L-00019": ("einmal", "Lieferung"), "L-00067": ("einmal", "Lieferung"),
    "L-00083": ("einmal", "Lieferung"), "L-00145": ("einmal", "Lieferung"),
    "L-00096": ("einmal", "Muster"), "L-00100": ("einmal", "Muster"), "L-00103": ("einmal", "Muster"),
}

# Notfalleinsätze (Ausreisser): Lieferzeile, Lieferdatum, IBC
NOTFALL = [("L-00020", "2022-08-16", 18), ("L-00063", "2024-03-11", 20), ("L-00141", "2026-09-22", 24)]

# K-1003 Verladestation: P-103 bis März 2026, Erprobung P-203 am 12.04.2026, dann wieder P-103.
K1003_VERLADESTATION = "L-00014"
K1003_VERLADE_LETZTE_VOR_TEST = "2026-02-24"
K1003_ERPROBUNG = "L-00019"
K1003_ERPROBUNG_AUFTRAG = "2026-03-27"
K1003_KULANZ = "2026-06-24"
K1003_NACHBESTELLUNG = "2026-07-10"  # Akte D17: Bestellung AR-AFFF, Lieferung 17.07.2026

# Stationäre Anlagen mit Datenaufnahme: feste Auswahl plus Hash; Verladestation nie.
DATENAUFNAHME_FEST = {"L-00028": "2023-05-16", "L-00091": "2024-03-19", "L-00137": "2025-02-11",
                      "L-00138": "2024-09-24", "L-00146": "2025-05-20", "L-00147": "2024-04-23"}
DATENAUFNAHME_NIE = {"L-00014", "L-00135", "L-00015"}
DATENAUFNAHME_ZIEL = 11  # von 37 stationären Anlagen, ca. 30 %


def produktlinie(p: dict) -> str:
    b = p["basis"]
    if b.startswith("fluorfrei"):
        return "fluorfrei"
    if b == "Netzmittel":
        return "offen"
    return "fluorhaltig"


def listenpreis(pid: str, gebinde: str, jahr: int) -> float:
    basis = PREIS_L_2026[pid] * GEBINDE_FAKTOR[gebinde] * GEBINDE_L[gebinde]
    return round(basis * PREISINDEX[jahr], 2)


def preisschutz_2026(weg: str, auftragsdatum: date) -> float:
    """Preiserhöhung 2026 (+4 % Liste) nur teilweise durchgesetzt: Faktor auf den Nettopreis.

    Rahmenverträge: Preise das ganze Jahr auf Vorjahresniveau; Händler: Sonderrabatt 2,5 %;
    direkte Kunden: Aufträge bis 31.03.2026 noch zum Vorjahrespreis. Notfallservice: kein Preisschutz.
    """
    if weg == "Rahmenvertrag":
        return PREISINDEX[2025]
    if weg == "Händler":
        return PREISSCHUTZ_HAENDLER
    if weg == "direkt" and auftragsdatum < PREISSCHUTZ_DIREKT_BIS:
        return PREISINDEX[2025]
    return 1.0


def gebinde_fuer(pid: str) -> list:
    g = ["Kanister", "Fass", "IBC"]
    if pid in LOSE_WARE:
        g.append("l")
    return g


# --------------------------------------------------------------------------
# Tabellen
# --------------------------------------------------------------------------


def baue_kunden(kunden: list) -> list:
    zeilen = []
    for k in kunden:
        a = k["ansprechpartner"]
        zeilen.append({
            "id": k["id"], "name": k["name"], "segment": k["segment"], "land": k["land"],
            "sprache": k["sprache"], "ansprechpartner_name": a["name"],
            "ansprechpartner_rolle": a["rolle"], "ansprechpartner_email": a["email"],
            "key_account": _ja(k["key_account"]), "ist_haendler": _ja(k["ist_haendler"]),
            "beliefert_endkunden": ";".join(k["beliefert_endkunden"]), "status": k["status"],
        })
    return zeilen


def baue_produkte(produkte: list) -> list:
    zeilen = []
    for p in produkte:
        zeilen.append({
            "id": p["id"], "name": p["name"], "schaumart": p["schaumart"],
            "brandklassen": ";".join(p["brandklassen"]), "einsatzbereiche": ";".join(p["einsatzbereiche"]),
            "basis": p["basis"], "produktlinie": produktlinie(p),
            "fluorfrei_deklariert": _ja(p["fluorfrei_deklariert"]),
            "zumischrate_prozent": _zahl(p["zumischrate_prozent"], 1),
            "nachfolger_id": p["nachfolger_id"] or "", "status": p["status"],
            "eingefuehrt_am": EINFUEHRUNG[p["id"]], "ausgelaufen_am": "",
        })
    return zeilen


def lieferstellen_index(lieferungen: list) -> tuple[dict, dict]:
    """(kunde, anlage) -> LS-ID in Reihenfolge des ersten Auftretens; Lieferzeile -> LS-ID."""
    ls_von = {}
    zeile_ls = {}
    for l in lieferungen:
        schluessel = (l["kunde_id"], l["anlage"])
        if schluessel not in ls_von:
            ls_von[schluessel] = "LS-%04d" % (len(ls_von) + 1)
        zeile_ls[l["id"]] = ls_von[schluessel]
    return ls_von, zeile_ls


def baue_lieferstellen(lieferungen: list, produkte: list) -> list:
    rate = {p["id"]: p["zumischrate_prozent"] for p in produkte}
    ls_von, zeile_ls = lieferstellen_index(lieferungen)
    gruppen = {}
    for l in lieferungen:
        gruppen.setdefault(zeile_ls[l["id"]], []).append(l)

    # Datenaufnahme: stationäre Anlagen
    stationaer = [l for l in lieferungen if l["anwendung"] == "stationaere_anlage"]
    datenaufnahme = dict(DATENAUFNAHME_FEST)
    kandidaten = sorted((l for l in stationaer if l["id"] not in datenaufnahme
                         and l["id"] not in DATENAUFNAHME_NIE), key=lambda l: _h("da", l["id"]))
    for l in kandidaten:
        if len(datenaufnahme) >= DATENAUFNAHME_ZIEL:
            break
        datenaufnahme[l["id"]] = _tage(_d("2023-03-01"), _d("2027-02-19"), "da-datum", l["id"]).isoformat()

    zeilen = []
    for ls_id in sorted(gruppen):
        g = gruppen[ls_id]
        aktuell = max(g, key=lambda l: (l["letzte_lieferung"], -g.index(l)))
        anw = g[0]["anwendung"]
        da = ""
        z_anlage = ""
        z_crm = ""
        if anw == "stationaere_anlage":
            l = g[0]
            soll = rate[l["produkt_id"]]
            z_crm = _zahl(soll, 1)
            if l["id"] == "L-00032":  # Altanlage: CRM führt noch die frühere Rate
                z_crm = "3.0"
            if l["id"] in datenaufnahme:
                da = datenaufnahme[l["id"]]
                gemessen = soll
                if _u("zm", l["id"]) < 0.25:
                    gemessen = soll + (0.5 if soll >= 1 else 0.1)
                z_anlage = _zahl(gemessen, 1)
        zeilen.append({
            "lieferstelle_id": ls_id, "kunde_id": g[0]["kunde_id"], "anlage": g[0]["anlage"],
            "anwendung": anw, "aktuelles_produkt_id": aktuell["produkt_id"],
            "fuellmenge_l": str(sum(x["menge_l"] for x in g)),
            "letzte_lieferung": max(x["letzte_lieferung"] for x in g),
            "datenaufnahme_am": da, "zumischrate_anlage": z_anlage, "zumischrate_crm": z_crm,
        })
    return zeilen


def baue_preisliste(produkte: list, jahr: int) -> list:
    zeilen = []
    for p in produkte:
        for g in gebinde_fuer(p["id"]):
            zeilen.append({"produkt_id": p["id"], "gebinde": g,
                           "preis_netto_eur": _zahl(listenpreis(p["id"], g, jahr)),
                           "gueltig_ab": "%d-01-01" % jahr})
    return zeilen


def _menge_einheit(pid: str, liter: float, anwendung: str, *schluessel: object) -> tuple[str, int]:
    """Liter -> (Einheit, Anzahl) nach Gebindelogik."""
    if liter >= 5000 and pid in LOSE_WARE and anwendung == "stationaere_anlage":
        return "l", max(500, int(round(liter / 500.0)) * 500)
    if liter >= 1000:
        return "IBC", max(1, int(round(liter / 1000.0)))
    if liter >= 200:
        return "Fass", max(1, int(round(liter / 200.0)))
    return "Kanister", max(1, int(round(liter / 20.0)))


FLUORFREI_IDS = {pid for pid in PREIS_L_2026 if pid >= "P-2" or pid in
                 ("P-110", "P-111", "P-112", "P-114", "P-115", "P-116", "P-118", "P-119")}


def _trend(pid: str, anwendung: str, jahr: int) -> float:
    if pid in FLUORFREI_IDS:
        return TREND_FLUORFREI[jahr]
    if anwendung == "stationaere_anlage" or pid in ("P-107", "P-206"):
        return 1.0
    return TREND_FLUORHALTIG[jahr]


def _ereignisse_zeile(l: dict) -> list:
    """Lieferereignisse (datum, produkt, liter_wunsch, art, fest) einer Lieferzeile."""
    anw = l["anwendung"]
    ende = _d(l["letzte_lieferung"])
    verlauf = VERLAUF.get(l["id"])
    if verlauf and verlauf[0] == "einmal":
        return [(ende, l["produkt_id"], float(l["menge_l"]), verlauf[1], True)]

    start = START
    wechsel = None
    vorgaenger = None
    if verlauf and verlauf[0] == "start":
        start = _d(verlauf[1])
    elif verlauf and verlauf[0] == "wechsel":
        wechsel = _d(verlauf[1])
        vorgaenger = verlauf[2]

    ereignisse = []
    frequenz = FREQUENZ[anw] * (0.8 + 0.4 * _u("f", l["id"]))
    intervall = 365.0 / frequenz
    jahresmenge = l["menge_l"] * UMSCHLAG[anw] * (0.8 + 0.4 * _u("m", l["id"]))
    if l["kunde_id"] in ("K-1023", "K-1024"):
        jahresmenge *= HAENDLER_FAKTOR
    if ende < date(2026, 1, 1):
        jahresmenge *= FRUEHES_ENDE_FAKTOR

    letzte = ende
    if l["id"] == K1003_VERLADESTATION:
        letzte = _d(K1003_VERLADE_LETZTE_VOR_TEST)
        ereignisse.append((ende, l["produkt_id"], float(l["menge_l"]), "Lieferung", True))

    d = letzte
    i = 0
    while d >= start:
        pid = l["produkt_id"]
        if wechsel is not None and d < wechsel:
            pid = vorgaenger
        liter = jahresmenge / frequenz * (0.6 + 0.8 * _u("q", l["id"], i)) * _trend(pid, anw, d.year)
        ereignisse.append((d, pid, liter, "Lieferung", False))
        i += 1
        schritt = intervall * (0.55 + 0.9 * _u("t", l["id"], i))
        d = d - timedelta(days=max(7, int(round(schritt))))
    # Erstbefüllung, wenn die Lieferstelle im Zeitraum neu beliefert wird
    if start > START and ereignisse:
        erstes = min(ereignisse, key=lambda e: e[0])
        ereignisse.remove(erstes)
        ereignisse.append((erstes[0], erstes[1], float(l["menge_l"]), "Lieferung", False))
    return ereignisse


def baue_auftraege(kunden: list, produkte: list, lieferungen: list) -> list:
    kunde = {k["id"]: k for k in kunden}
    _, zeile_ls = lieferstellen_index(lieferungen)
    positionen = []  # vor Vergabe der Auftragsnummern

    def neue_position(l, lieferdatum, pid, menge, einheit, art, weg, auftragsdatum):
        k = kunde[l["kunde_id"]]
        jahr = lieferdatum.year
        gebinde = einheit
        if einheit not in gebinde_fuer(pid):
            gebinde = "IBC"
        preis_eur = listenpreis(pid, gebinde, jahr) if art != "Muster" else 0.0
        if einheit != gebinde:  # sollte nicht vorkommen
            preis_eur = 0.0
        if weg == "Händler":
            preis_eur *= 0.82
        elif weg == "Rahmenvertrag":
            preis_eur *= 0.92
        elif weg == "Notfallservice":
            preis_eur *= 1.35
        elif k["key_account"]:
            preis_eur *= 0.95
        if jahr == 2026 and art == "Lieferung" and l["id"] != K1003_ERPROBUNG:
            preis_eur *= preisschutz_2026(weg, auftragsdatum)
        waehrung = WAEHRUNG.get(k["id"], "EUR")
        preis = preis_eur
        if waehrung != "EUR":
            preis = preis_eur / KONZERNKURSE[str(jahr)][waehrung]
        preis = round(preis, 2)
        positionen.append({
            "auftragsdatum": auftragsdatum, "lieferdatum": lieferdatum, "kunde_id": l["kunde_id"],
            "lieferstelle_id": zeile_ls[l["id"]], "produkt_id": pid, "anwendung": l["anwendung"],
            "menge": menge, "einheit": einheit, "preis": preis, "waehrung": waehrung,
            "vertriebsweg": weg, "art": art, "zeile": l["id"],
        })

    def standardweg(kid):
        k = kunde[kid]
        if k["ist_haendler"]:
            return "Händler"
        if kid in RAHMENVERTRAG:
            return "Rahmenvertrag"
        return "direkt"

    for l in lieferungen:
        for (lieferdatum, pid, liter, art, fest) in _ereignisse_zeile(l):
            if lieferdatum < START:
                continue
            if l["kunde_id"] == "K-1029" and lieferdatum >= RUHEND_AB:
                continue
            if pid in EINFUEHRUNG and lieferdatum < _d(EINFUEHRUNG[pid]):
                continue
            if l["id"] == K1003_ERPROBUNG:
                einheit, menge = "Kanister", int(round(liter / 20))
            elif fest and liter >= 1000 and l["anwendung"] == "stationaere_anlage":
                einheit, menge = "l", int(liter)
            elif fest and art == "Muster":
                einheit, menge = "Kanister", int(round(liter / 20))
            else:
                einheit, menge = _menge_einheit(pid, liter, l["anwendung"], l["id"], lieferdatum)
            vorlauf = 2 + _h("v", l["id"], lieferdatum) % 11
            auftragsdatum = lieferdatum - timedelta(days=vorlauf)
            if l["id"] == K1003_ERPROBUNG:
                auftragsdatum = _d(K1003_ERPROBUNG_AUFTRAG)
            if l["id"] == K1003_VERLADESTATION and lieferdatum == _d(l["letzte_lieferung"]):
                auftragsdatum = _d(K1003_NACHBESTELLUNG)
            if auftragsdatum < START:
                auftragsdatum = START
            weg = "direkt" if art == "Muster" else standardweg(l["kunde_id"])
            neue_position(l, lieferdatum, pid, menge, einheit, art, weg, auftragsdatum)

    zeile_von = {l["id"]: l for l in lieferungen}
    for (zid, datum, ibc) in NOTFALL:
        l = zeile_von[zid]
        lieferdatum = _d(datum)
        neue_position(l, lieferdatum, l["produkt_id"], ibc, "IBC", "Lieferung", "Notfallservice",
                      lieferdatum - timedelta(days=1))

    # Gutschriften und Retouren (negativ); Kulanz Raffinerie fest
    gutschriften = []
    for p in positionen:
        if p["art"] != "Lieferung" or p["vertriebsweg"] == "Notfallservice":
            continue
        u = _u("gs", p["zeile"], p["lieferdatum"])
        if u < 0.008:
            art = "Retoure"
        elif u < 0.014:
            art = "Gutschrift"
        else:
            continue
        datum = p["lieferdatum"] + timedelta(days=8 + _h("gsd", p["zeile"], p["lieferdatum"]) % 30)
        if datum > STICHTAG or (p["kunde_id"] == "K-1029" and datum >= RUHEND_AB):
            continue
        menge = p["menge"] if art == "Gutschrift" else max(1, p["menge"] // 3)
        q = dict(p)
        q.update({"auftragsdatum": datum, "lieferdatum": datum, "menge": -menge, "art": art})
        gutschriften.append(q)
    for p in positionen:
        if p["zeile"] == K1003_ERPROBUNG:
            q = dict(p)
            q.update({"auftragsdatum": _d(K1003_KULANZ), "lieferdatum": _d(K1003_KULANZ),
                      "menge": -p["menge"], "art": "Gutschrift"})
            gutschriften.append(q)
    positionen.extend(gutschriften)

    # Auftragsnummern: je Kunde, Auftragsdatum, Vertriebsweg und Art ein Auftrag
    positionen.sort(key=lambda p: (p["auftragsdatum"], p["kunde_id"], p["vertriebsweg"], p["art"],
                                   p["lieferstelle_id"], p["produkt_id"], p["lieferdatum"]))
    zaehler = {}
    auftrag_von = {}
    pos_zaehler = {}
    zeilen = []
    for p in positionen:
        schluessel = (p["auftragsdatum"], p["kunde_id"], p["vertriebsweg"], p["art"])
        if schluessel not in auftrag_von:
            jahr = p["auftragsdatum"].year
            alt = p["auftragsdatum"] < ERP_WECHSEL
            system = "alt" if alt else "neu"
            zaehler[(system, jahr)] = zaehler.get((system, jahr), 0) + 1
            n = zaehler[(system, jahr)]
            if alt:
                auftrag_von[schluessel] = "%02d%05d" % (jahr % 100, 300 + n * 3)
            else:
                auftrag_von[schluessel] = "AU-%d-%05d" % (jahr, n)
            pos_zaehler[schluessel] = 0
        pos_zaehler[schluessel] += 1
        alt = p["auftragsdatum"] < ERP_WECHSEL
        liter = p["menge"] * GEBINDE_L[p["einheit"]]
        menge_l = "" if (alt and p["einheit"] == "IBC") else str(liter)
        zeilen.append({
            "auftrag_id": auftrag_von[schluessel], "position": str(pos_zaehler[schluessel]),
            "auftragsdatum": p["auftragsdatum"].isoformat(), "lieferdatum": p["lieferdatum"].isoformat(),
            "kunde_id": p["kunde_id"], "lieferstelle_id": p["lieferstelle_id"],
            "produkt_id": p["produkt_id"], "anwendung": p["anwendung"], "menge": str(p["menge"]),
            "einheit": p["einheit"], "menge_l": menge_l,
            "preis_netto_je_einheit": _zahl(p["preis"]), "waehrung": p["waehrung"],
            "nettobetrag": _zahl(round(p["menge"] * p["preis"], 2)),
            "vertriebsweg": p["vertriebsweg"], "art": p["art"],
            "quellsystem": "ERP-alt" if alt else "ERP-neu",
        })

    # Doppelimporte: ca. 1 % der Positionen, vor allem aus der Migration (ERP-alt)
    doppelt = []
    for z in zeilen:
        schwelle = 0.022 if z["quellsystem"] == "ERP-alt" else 0.002
        if _u("dup", z["auftrag_id"], z["position"]) < schwelle and z["kunde_id"] != "K-1029":
            doppelt.append(dict(z))
    # Doppelte stehen hinter dem letzten ERP-alt-Auftrag (Migrationslauf), danach ERP-neu
    alt = [z for z in zeilen if z["quellsystem"] == "ERP-alt"]
    neu = [z for z in zeilen if z["quellsystem"] == "ERP-neu"]
    return alt + doppelt + neu


# --------------------------------------------------------------------------
# Reklamationen und Kontakte (P1)
# --------------------------------------------------------------------------

# Feste Reklamationen: (eingang, kunde, produkt, kategorie, auto, tage, status)
REKLAMATIONEN_FEST = [
    # Probeumstellungen 2025
    ("2025-06-23", "K-1014", "P-204", "Probeumstellung", False, 6, "abgeschlossen"),
    ("2025-07-21", "K-1011", "P-201", "Probeumstellung", False, 4, "abgeschlossen"),
    ("2025-07-14", "K-1031", "P-203", "Probeumstellung", False, 8, "abgeschlossen"),
    ("2025-11-03", "K-1005", "P-207", "Probeumstellung", True, 0, "abgeschlossen"),
    # Probeumstellungen 2026 bis zum Memo (7 im ganzen Unternehmen)
    ("2026-01-20", "K-1005", "P-207", "Probeumstellung", False, 5, "abgeschlossen"),
    ("2026-02-24", "K-1015", "P-205", "Probeumstellung", True, 0, "abgeschlossen"),
    ("2026-03-10", "K-1021", "P-202", "Probeumstellung", False, 7, "abgeschlossen"),
    ("2026-04-02", "K-1002", "P-201", "Probeumstellung", True, 0, "abgeschlossen"),
    ("2026-05-08", "K-1003", "P-203", "Probeumstellung", True, 0, "abgeschlossen (Kulanz)"),
    ("2026-05-19", "K-1003", "P-203", "Probeumstellung", False, 10, "abgeschlossen (Kulanz)"),
    ("2026-05-27", "K-1022", "P-202", "Probeumstellung", True, 0, "abgeschlossen"),
    # danach
    ("2026-07-02", "K-1020", "P-202", "Probeumstellung", False, 3, "abgeschlossen"),
    ("2026-07-08", "K-1024", "P-201", "Probeumstellung", False, 4, "abgeschlossen"),
    ("2027-01-26", "K-1017", "P-204", "Probeumstellung", False, 5, "in Bearbeitung"),
    ("2027-02-15", "K-1019", "P-204", "Probeumstellung", False, 3, "offen"),
]
KATEGORIEN = ["Schaumqualität", "Lieferung/Menge", "Gebinde/Verpackung", "Rechnung", "Dokumentation"]
REKLAMATIONEN_ZUSATZ = 36
R2026_VOR_RAFFINERIE_ZUSATZ = 3  # + 4 feste Probeumstellungen = 7 Meldungen vor R-2026-008


def baue_reklamationen(auftraege: list) -> list:
    faelle = list(REKLAMATIONEN_FEST)
    # Kandidaten: echte Lieferungen 2024-2027 (ohne K-1003 Pumpenstation, ohne Muster)
    kandidaten = []
    gesehen = set()
    for z in auftraege:
        if z["art"] != "Lieferung" or z["lieferdatum"] < "2023-12-01":
            continue
        if z["kunde_id"] == "K-1003" and z["produkt_id"] == "P-119":
            continue
        schluessel = (z["auftrag_id"], z["position"])
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        kandidaten.append(z)
    kandidaten.sort(key=lambda z: _h("rk", z["auftrag_id"], z["position"]))
    vor_r008 = 0  # Akte: Portalmeldung vom 08.05.2026 ist R-2026-008, Brief vom 19.05.2026 R-2026-009
    for z in kandidaten:
        if len(faelle) >= len(REKLAMATIONEN_FEST) + REKLAMATIONEN_ZUSATZ:
            break
        eingang = _d(z["lieferdatum"]) + timedelta(days=3 + _h("rke", z["auftrag_id"]) % 35)
        if eingang < date(2024, 1, 2) or eingang > date(2027, 2, 26):
            continue
        if date(2026, 5, 8) <= eingang <= date(2026, 5, 19):
            continue
        if date(2026, 1, 1) <= eingang < date(2026, 5, 8):
            if vor_r008 >= R2026_VOR_RAFFINERIE_ZUSATZ:
                continue
            vor_r008 += 1
        kat = KATEGORIEN[_h("rkk", z["auftrag_id"]) % len(KATEGORIEN)]
        auto = PORTAL_ASSISTENT_AB <= eingang < RL_REKLAMATION_V11_AB and _u("rka", z["auftrag_id"]) < 0.55
        tage = 0 if auto else 1 + _h("rkt", z["auftrag_id"]) % (9 if eingang < RL_REKLAMATION_V11_AB else 5)
        if eingang >= date(2027, 2, 1):
            status = "offen"
        elif auto and _u("rks", z["auftrag_id"]) < 0.5:
            status = "abgelehnt"
        elif _u("rks2", z["auftrag_id"]) < 0.15:
            status = "abgeschlossen (Kulanz)"
        else:
            status = "abgeschlossen"
        faelle.append((eingang.isoformat(), z["kunde_id"], z["produkt_id"], kat, auto, tage, status))
    faelle.sort(key=lambda f: (f[0], f[1], f[2]))
    zeilen = []
    zaehler = {}
    for (eingang, kid, pid, kat, auto, tage, status) in faelle:
        jahr = eingang[:4]
        zaehler[jahr] = zaehler.get(jahr, 0) + 1
        zeilen.append({
            "rekl_id": "R-%s-%03d" % (jahr, zaehler[jahr]), "eingang": eingang, "kunde_id": kid,
            "produkt_id": pid, "kategorie": kat, "auto_beantwortet": _ja(auto),
            "tage_bis_antwort": str(tage), "status": status,
        })
    return zeilen


# Kontakte K-1003: (datum, kanal, richtung, bearbeitung, betreff, dokument)
# Dateinamen = Dokumente der Akte tag1/akten/K-1003 Raffinerie Kuestenmark/ (Abgleich: _akte_dokumente.txt)
AT = "Jannik Thormählen (Außendienst-Anwendungstechnik)"
BL = "Birte Lohmeyer (Teamleitung Anwendungstechnik & Kundendienst)"
KONTAKTE_K1003 = [
    ("2024-02-20", "Besuch", "ausgehend", AT, "Jahresgespräch Werkfeuerwehr", ""),
    ("2024-06-04", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung AR-AFFF Tanklager", ""),
    ("2024-09-17", "Telefon", "ausgehend", AT, "Vorstellung Umstellungsprogramm FreeFoam", ""),
    ("2024-11-05", "Besuch", "ausgehend", AT, "Begehung Tankfeld 1", ""),
    ("2025-03-12", "E-Mail", "ausgehend", "Vertrieb", "Einladung Fachtag fluorfreie Schaummittel", ""),
    ("2025-07-08", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung AR-AFFF Tankfeld 1", ""),
    ("2025-11-20", "Besuch", "ausgehend", AT, "Jahresgespräch 2026, Interesse an Erprobung fluorfrei", ""),
    ("2026-02-26", "Telefon", "eingehend", AT, "Anfrage Erprobungsmenge Verladestation", ""),
    ("2026-03-03", "System", "intern", AT, "CRM-Auszug Anlage Verladestation",
     "D02 2026-03-03 CRM-Auszug Anlage Verladestation.md"),
    ("2026-03-03", "E-Mail", "ausgehend", AT, "Angebot Erprobungsmenge FreeFoam AR 3x3",
     "D01 2026-03-03 Mail Angebot Erprobungsmenge.eml"),
    ("2026-03-27", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung Erprobungsmenge", ""),
    ("2026-04-12", "Lieferschein", "ausgehend", "Versand Werk Nord", "Lieferung Erprobungsmenge",
     "D03 2026-04-12 Lieferschein Erprobungsmenge.md"),
    ("2026-04-27", "Telefon", "eingehend", AT, "Termin Probeverschäumung", ""),
    ("2026-05-07", "Kundenportal", "eingehend", "Kundenportal", "Prüfprotokoll Probeverschäumung (Anhang zur Reklamation)",
     "D04 2026-05-07 Pruefprotokoll Probeverschaeumung.md"),
    ("2026-05-08", "Kundenportal", "eingehend", "Kundenportal", "Reklamation Probeverschäumung Verladestation",
     "D05 2026-05-08 Reklamation Kundenportal.md"),
    ("2026-05-08", "E-Mail", "ausgehend", "Kundenportal (Assistent, automatisch)", "Antwort auf Reklamation",
     "D06 2026-05-08 Mail Antwort Portal-Assistent.eml"),
    ("2026-05-11", "Telefon", "eingehend", AT, "Telefonat mit Leiter Brandschutz zur Reklamation",
     "D07 2026-05-11 Telefonnotiz Aussendienst.md"),
    ("2026-05-12", "E-Mail", "intern", BL, "Auftrag Labor: Rückstellmuster und Tankprobe",
     "D08 2026-05-12 Mail Teamleitung an Labor.eml"),
    ("2026-05-15", "Brief", "eingehend", "Geschäftsführung", "Schreiben des Sachversicherers an den Kunden (Anlage zum Brief vom 19.05.)",
     "D09 2026-05-15 Schreiben Sachversicherer.md"),
    ("2026-05-19", "Brief", "eingehend", "Geschäftsführung", "Reklamation der Werkleiterin an die Geschäftsführung",
     "D10 2026-05-19 Brief Kunde an Geschaeftsfuehrung.md"),
    ("2026-05-20", "Bericht", "intern", "Labor Schaumanalyse", "Zwischenbefund Rückstellmuster",
     "D11 2026-05-20 Laborbefund Rueckstellmuster.md"),
    ("2026-05-21", "E-Mail", "intern", "Geschäftsführung", "Weiterleitung Brief der Werkleiterin",
     "D12 2026-05-21 Mail Geschaeftsfuehrerin an Teamleitung.eml"),
    ("2026-05-29", "Brief", "ausgehend", BL, "Antwort auf die Reklamationen",
     "D13 2026-05-29 Antwortschreiben an Kunden (versandt).md"),
    ("2026-06-03", "Bericht", "intern", "Labor Schaumanalyse", "Laborbericht Tankprobe und Zumischung",
     "D14 2026-06-03 Laborbericht Tankprobe und Zumischung.md"),
    ("2026-06-05", "Memo", "intern", "Dr. Henrike Vossberg (Programmleitung Fluorfrei-Umstellung)",
     "Memo Probeumstellungen 2026", "D15 2026-06-05 Memo Programmleitung.md"),
    ("2026-06-10", "Besuch", "ausgehend", BL, "Termin vor Ort mit Werkleitung",
     "D16 2026-06-10 Gespraechsnotiz Termin vor Ort.md"),
    ("2026-06-24", "System", "intern", "Buchhaltung", "Kulanzgutschrift Erprobungsmenge", ""),
    ("2026-07-10", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung AR-AFFF Verladestation",
     "D17 2026-07-10 Mail Bestellung AR-AFFF.eml"),
    ("2026-09-08", "Telefon", "ausgehend", AT, "Nachfassen: Datenaufnahme der Anlage angeboten", ""),
    ("2026-10-20", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung Werkfeuerwehr Großlöschfahrzeug", ""),
    ("2026-12-03", "E-Mail", "ausgehend", AT, "Termin Jahresgespräch 2027", ""),
    ("2026-12-08", "E-Mail", "eingehend", "Vertriebsinnendienst", "Bestellung Werkfeuerwehr TLF Reserve", ""),
    ("2027-01-19", "Besuch", "ausgehend", AT, "Jahresgespräch 2027", ""),
    ("2027-02-16", "Telefon", "ausgehend", AT, "Terminvorschlag Datenaufnahme Verladestation", ""),
]


def baue_kontakte() -> list:
    zeilen = []
    for (datum, kanal, richtung, bearbeitung, betreff, dokument) in KONTAKTE_K1003:
        zeilen.append({"datum": datum, "kunde_id": "K-1003", "kanal": kanal, "richtung": richtung,
                       "bearbeitung": bearbeitung, "betreff": betreff, "dokument": dokument})
    return zeilen


def baue_akte_liste() -> str:
    teile = ["# Vorgesehene Dokumente der Akte tag1/akten/K-1003 Raffinerie Kuestenmark/",
             "# (aus kontakte.csv, Feld dokument; erzeugt von werkzeuge/erzeuge_daten.py)"]
    for k in KONTAKTE_K1003:
        if k[5]:
            teile.append(k[5])
    return "\n".join(teile) + "\n"


def baue_kennzahlen() -> dict:
    return {
        "stichtag": STICHTAG.isoformat(),
        "heute": HEUTE.isoformat(),
        "waehrung_konzern": "EUR",
        "konzernkurse": {"hinweis": "1 Einheit Fremdwährung = x EUR, Jahresdurchschnitt; 2027 = Kurs 2026",
                         "kurse": KONZERNKURSE},
        "ziele": {"fluorfrei_anteil": {"2026": 0.60, "2027": 0.80}},
        "definitionen": {
            "fluorfrei_anteil": {
                "formel": "Liter der fluorfreien Produktlinie / alle gelieferten Liter im Kalenderjahr",
                "zaehler": "Positionen mit produkte.produktlinie = 'fluorfrei'",
                "nenner": "alle Positionen (alle Produktlinien)",
                "jahr": "nach Lieferdatum (Kalenderjahr)",
                "netto": "Gutschriften und Retouren mit ihren negativen Mengen abziehen",
                "ohne": ["Muster (art = 'Muster')", "Doppelimporte (gleiche auftrag_id und position nur einmal zählen)"],
                "liter": "menge_l; fehlt es, menge x Gebindegröße (umrechnung_gebinde)",
                "hinweis": "Die Deklaration (produkte.fluorfrei_deklariert) ist nicht die Grundlage der Kennzahl.",
            },
            "aktiver_kunde": "mindestens ein Auftrag (art = 'Lieferung') in den 24 Monaten vor dem Stichtag",
            "umrechnung_gebinde": {"IBC": 1000, "Fass": 200, "Kanister": 20, "l": 1},
            "deckungsbeitrag": {
                "formel": "Deckungsbeitrag = Nettoumsatz - Herstellkosten - Fracht; DB-Marge = Deckungsbeitrag / Nettoumsatz",
                "nettoumsatz": "Summe nettobetrag aller Positionen (Lieferungen, Gutschriften und Retouren negativ, "
                               "Muster 0) in EUR, ohne Doppelimporte, Jahr nach Lieferdatum",
                "herstellkosten": "Liter x (rohstoff_eur_l + fertigung_eur_l) aus herstellkosten.csv für Produkt und "
                                  "Lieferjahr; für Lieferungen und Muster, Retouren mindern (Ware kommt zurück); "
                                  "Gutschriften ohne Herstellkosten (Ware bleibt beim Kunden)",
                "fracht": "fracht.csv je Auftrag; auf die Positionen des Auftrags nach Litern verteilt, "
                          "Jahr nach Lieferdatum der Position",
                "hinweis": "Margen und Quoten aus den Summen bilden, nie Prozentwerte mitteln.",
            },
            "umrechnung_fremdwaehrung": {
                "ist_berichte": "Konzernkurs des Lieferjahres (konzernkurse)",
                "plan_ist_2026": "Budget ist zum Plankurs gerechnet; Ist zum Ist-Monatskurs des Liefermonats (kurse.csv)",
                "fremdwaehrungseffekt": "Ist-Betrag in Fremdwährung x (Ist-Monatskurs - Plankurs)",
            },
            "rabattquote": {
                "formel": "1 - Summe nettobetrag (EUR) / Summe Listenwert",
                "listenwert": "menge x Listenpreis des gleichen Gebindes (einheit 'l' = lose) aus der Preisliste "
                              "des Lieferjahres",
                "positionen": "art = 'Lieferung', ohne Notfallservice (Zuschlag statt Rabatt), ohne Doppelimporte",
                "fremdwaehrung": "zum Konzernkurs des Lieferjahres in EUR",
                "jahre": "nur 2025 und 2026 (für frühere Jahre gibt es keine Preisliste im Ausschnitt)",
            },
            "plan_ist_bruecke": {
                "zellen": "Produktlinie x Segment, Kalenderjahr 2026",
                "ist": "netto Liter wie fluorfrei_anteil; Umsatz und Kosten wie deckungsbeitrag; "
                       "Notfallservice nicht in den Zellen, sondern als eigener Balken (nicht budgetiert)",
                "mengeneffekt": "(Ist-Liter gesamt - Plan-Liter gesamt) x Plan-Durchschnitt je Liter",
                "mixeffekt": "Summe je Zelle (Ist-Liter x Plan-Wert je Liter) - Ist-Liter gesamt x Plan-Durchschnitt je Liter",
                "preiseffekt": "Summe je Zelle (Ist-Umsatz zum Plankurs - Ist-Liter x Plan-Preis je Liter)",
                "kosteneffekt": "nur Deckungsbeitrag: Summe je Zelle (Ist-Liter x Plan-Kosten je Liter - Ist-Kosten); "
                                "Plan-Kosten je Liter = Plan-Preis - Plan-DB je Liter",
                "fremdwaehrungseffekt": "wie umrechnung_fremdwaehrung, ohne Notfallservice",
                "wert_je_liter": "Umsatzbrücke: Umsatz je Liter; DB-Brücke: Deckungsbeitrag je Liter",
            },
        },
        "ampel_regel": {
            "grundlage": "Anteil fluorhaltiger Liter (produktlinie = 'fluorhaltig') je Segment und Land, Kalenderjahr",
            "rot": "> 0.50",
            "gelb": "0.20 bis 0.50 (beide Grenzen eingeschlossen)",
            "gruen": "< 0.20",
            "luecke": "weniger als 20 Positionen: keine Ampel, als Lücke zeigen",
        },
    }


# --------------------------------------------------------------------------
# Finanzdaten (Drill 2): Herstellkosten, Fracht, Kurse, Budget 2026
# --------------------------------------------------------------------------

# Herstellkosten je Liter: Rohstoff als Anteil am Listenpreis 2026 je Liter, Fertigung fest.
# Fluorfreie Rezepturen brauchen teurere Rohstoffe (Tenside, Polysaccharide) -> geringere Marge.
HK_ROHSTOFF_ANTEIL = {"fluorhaltig": 0.31, "fluorfrei": 0.47, "offen": 0.40}
HK_FERTIGUNG_L = {"fluorhaltig": 0.42, "fluorfrei": 0.56, "offen": 0.48}
HK_INDEX = {2021: 0.86, 2022: 0.97, 2023: 1.03, 2024: 1.00, 2025: 0.98, 2026: 1.0, 2027: 1.01}
HK_JAHRE = list(range(2021, 2028))

# Fracht je Sendung (= je Auftrag): Grundbetrag EUR, EUR je Liter
LAND_ZONE = {"DE": "Inland", "AT": "EU", "NL": "EU", "PL": "EU", "NO": "Drittland", "GB": "Drittland",
             "CH": "Drittland"}
FRACHT_TARIF = {"Inland": (35.0, 0.085), "EU": (65.0, 0.150), "Drittland": (95.0, 0.220)}
FRACHT_TANKWAGEN = {"Inland": (180.0, 0.045), "EU": (290.0, 0.070), "Drittland": (420.0, 0.110)}
FRACHT_PAKET = 28.0
FRACHT_EXPRESS = 2.5

# Kurse 2026: 1 Einheit Fremdwährung = x EUR. Plankurs aus dem Budget (Herbst 2025),
# Ist-Monatskurse schwanken um den Konzernkurs 2026 (Durchschnitt der zwölf Monate = Konzernkurs).
PLANKURSE_2026 = {"CHF": 1.040, "GBP": 1.190, "NOK": 0.0900}
KURS_ABWEICHUNG_2026 = {
    "CHF": [-0.011, -0.009, -0.007, -0.005, -0.002, 0.0, 0.001, 0.003, 0.005, 0.007, 0.008, 0.010],
    "GBP": [0.012, 0.010, 0.007, 0.005, 0.003, 0.001, -0.001, -0.003, -0.005, -0.007, -0.010, -0.012],
    "NOK": [0.0018, 0.0015, 0.0012, 0.0008, 0.0005, 0.0002, -0.0002, -0.0005, -0.0008, -0.0012, -0.0015,
            -0.0018],
}
KURS_STELLEN = {"CHF": 4, "GBP": 4, "NOK": 5}

# Budget 2026 (aufgestellt im Herbst 2025 aus dem Ist 2025): Wachstum je Segment, Fluorfrei-Ziel 60 %,
# Nettopreise wie Ist 2025 (Preiserhöhung nicht eingeplant), Kosten = Herstellkosten 2026 beim Produktmix 2025 + Fracht je Liter 2025.
BUDGET_WACHSTUM = {"Händler": 1.10, "Löschgerätehersteller": 1.08, "Übungsanlage": 1.06,
                   "Feuerwehr kommunal": 1.03, "Forst und Waldbrand": 1.02}
BUDGET_FLUORFREI_ZIEL = 0.60
BUDGET_PREIS_FAKTOR = 1.0
BUDGET_SAISON = [0.086, 0.084, 0.092, 0.090, 0.092, 0.087, 0.075, 0.087, 0.078, 0.092, 0.068, 0.069]
LINIEN = ["fluorhaltig", "fluorfrei", "offen"]


def baue_herstellkosten(produkte: list) -> list:
    zeilen = []
    for p in sorted(produkte, key=lambda x: x["id"]):
        linie = produktlinie(p)
        streuung = 0.92 + 0.16 * _u("hk", p["id"])
        roh26 = PREIS_L_2026[p["id"]] * HK_ROHSTOFF_ANTEIL[linie] * streuung
        fert26 = HK_FERTIGUNG_L[linie] * (0.95 + 0.10 * _u("hkf", p["id"]))
        for j in HK_JAHRE:
            zeilen.append({"produkt_id": p["id"], "jahr": str(j),
                           "rohstoff_eur_l": _zahl(roh26 * HK_INDEX[j], 3),
                           "fertigung_eur_l": _zahl(fert26 * (1 + 0.02 * (j - 2026)), 3)})
    return zeilen


def _liter_z(z: dict) -> int:
    if z["menge_l"] != "":
        return int(z["menge_l"])
    return int(z["menge"]) * GEBINDE_L[z["einheit"]]


def _eindeutig(auftraege: list) -> list:
    gesehen = set()
    aus = []
    for z in auftraege:
        s = (z["auftrag_id"], z["position"])
        if s not in gesehen:
            gesehen.add(s)
            aus.append(z)
    return aus


def baue_fracht(auftraege: list, kunden: list) -> list:
    """Eine Zeile je Auftrag mit Lieferungen oder Mustern (Gutschriften/Retouren ohne Fracht)."""
    land = {k["id"]: k["land"] for k in kunden}
    auftrag = {}
    for z in _eindeutig(auftraege):
        if z["art"] not in ("Lieferung", "Muster"):
            continue
        a = auftrag.setdefault(z["auftrag_id"], {"datum": z["lieferdatum"], "kunde": z["kunde_id"], "liter": 0,
                                                 "lose": False, "weg": z["vertriebsweg"], "art": z["art"]})
        a["datum"] = min(a["datum"], z["lieferdatum"])
        a["liter"] += _liter_z(z)
        a["lose"] = a["lose"] or z["einheit"] == "l"
    zeilen = []
    for aid, a in auftrag.items():
        zone = LAND_ZONE[land[a["kunde"]]]
        streuung = 0.93 + 0.14 * _u("fr", aid)
        if a["art"] == "Muster" or a["liter"] <= 60:
            versandart, betrag = "Paket", FRACHT_PAKET
        elif a["lose"]:
            grund, je_l = FRACHT_TANKWAGEN[zone]
            versandart, betrag = "Tankwagen", (grund + je_l * a["liter"]) * streuung
        else:
            grund, je_l = FRACHT_TARIF[zone]
            versandart, betrag = "Stückgut", (grund + je_l * a["liter"]) * streuung
        if a["weg"] == "Notfallservice":
            versandart, betrag = "Express", betrag * FRACHT_EXPRESS
        zeilen.append({"auftrag_id": aid, "versanddatum": a["datum"], "kunde_id": a["kunde"],
                       "versandart": versandart, "liter": str(a["liter"]), "frachtkosten_eur": _zahl(betrag)})
    return zeilen


def ist_kurs_2026(waehrung: str, monat: int) -> float:
    basis = KONZERNKURSE["2026"][waehrung]
    return round(basis + KURS_ABWEICHUNG_2026[waehrung][monat - 1], KURS_STELLEN[waehrung])


def baue_kurse() -> list:
    zeilen = []
    for m in range(1, 13):
        for w in ("CHF", "GBP", "NOK"):
            st = KURS_STELLEN[w]
            zeilen.append({"monat": "2026-%02d" % m, "waehrung": w,
                           "ist_kurs_eur": _zahl(ist_kurs_2026(w, m), st),
                           "plankurs_eur": _zahl(PLANKURSE_2026[w], st)})
    return zeilen


def _hk_je_l(herstellkosten: list) -> dict:
    return {(z["produkt_id"], int(z["jahr"])): float(z["rohstoff_eur_l"]) + float(z["fertigung_eur_l"])
            for z in herstellkosten}


def baue_budget(auftraege: list, kunden: list, produkte: list, herstellkosten: list, fracht: list) -> list:
    """Budget 2026 je Monat x Produktlinie x Segment, abgeleitet aus dem Ist 2025."""
    segment = {k["id"]: k["segment"] for k in kunden}
    linie = {p["id"]: produktlinie(p) for p in produkte}
    hk = _hk_je_l(herstellkosten)
    # Fracht 2025 je Liter und Segment (nur Lieferungen)
    fr_seg = {}
    for f in fracht:
        if f["versanddatum"][:4] == "2025" and f["versandart"] != "Express":
            s = segment[f["kunde_id"]]
            b, l = fr_seg.get(s, (0.0, 0))
            fr_seg[s] = (b + float(f["frachtkosten_eur"]), l + int(f["liter"]))
    # Ist 2025 je Zelle: Liter, Umsatz EUR (Konzernkurs 2025), Liter je Produkt
    liter = {}
    umsatz = {}
    mix = {}
    for z in _eindeutig(auftraege):
        if z["lieferdatum"][:4] != "2025" or z["art"] == "Muster" or z["vertriebsweg"] == "Notfallservice":
            continue
        c = (linie[z["produkt_id"]], segment[z["kunde_id"]])
        lt = _liter_z(z)
        kurs = 1.0 if z["waehrung"] == "EUR" else KONZERNKURSE["2025"][z["waehrung"]]
        liter[c] = liter.get(c, 0) + lt
        umsatz[c] = umsatz.get(c, 0.0) + float(z["nettobetrag"]) * kurs
        mix.setdefault(c, {})
        mix[c][z["produkt_id"]] = mix[c].get(z["produkt_id"], 0) + lt
    segmente = sorted({c[1] for c in liter})
    # Linienmittel als Ersatz für leere Zellen
    def linien_mittel(li):
        lt = sum(v for c, v in liter.items() if c[0] == li)
        um = sum(v for c, v in umsatz.items() if c[0] == li)
        pm = {}
        for c, m in mix.items():
            if c[0] == li:
                for pid, v in m.items():
                    pm[pid] = pm.get(pid, 0) + v
        return um / lt, pm
    # Planmenge je Segment und Fluorfrei-Anteil (Ziel 60 % über alle Liter)
    plan_seg = {}
    ff25 = {}
    offen25 = {}
    for s in segmente:
        ges = sum(liter.get((li, s), 0) for li in LINIEN)
        plan_seg[s] = ges * BUDGET_WACHSTUM.get(s, 1.0)
        ff25[s] = liter.get(("fluorfrei", s), 0) / ges
        offen25[s] = liter.get(("offen", s), 0) / ges
    gesamt = sum(plan_seg.values())
    # Anteil fluorhaltig je Segment = (1 - ff - offen) * lam; lam so, dass Fluorfrei gesamt = Ziel
    fh = sum(plan_seg[s] * (1 - ff25[s] - offen25[s]) for s in segmente)
    ff = sum(plan_seg[s] * ff25[s] for s in segmente)
    of = sum(plan_seg[s] * offen25[s] for s in segmente)
    lam = (gesamt - of - BUDGET_FLUORFREI_ZIEL * gesamt) / fh if fh else 0.0
    zeilen = []
    for s in segmente:
        anteil = {"fluorhaltig": (1 - ff25[s] - offen25[s]) * lam, "offen": offen25[s]}
        anteil["fluorfrei"] = 1 - anteil["fluorhaltig"] - anteil["offen"]
        b, l = fr_seg.get(s, (0.0, 0))
        fracht_l = b / l if l else 0.15
        for li in LINIEN:
            jahr_l = plan_seg[s] * anteil[li]
            if jahr_l < 1:
                continue
            c = (li, s)
            if liter.get(c, 0) > 0:
                preis25 = umsatz[c] / liter[c]
                pm = mix[c]
            else:
                preis25, pm = linien_mittel(li)
            preis = round(preis25 * BUDGET_PREIS_FAKTOR, 2)
            pl = sum(pm.values())
            kosten_l = sum(hk[(pid, 2026)] * v for pid, v in pm.items()) / pl + fracht_l
            for m in range(12):
                menge = int(round(jahr_l * BUDGET_SAISON[m] / 10.0)) * 10
                if menge <= 0:
                    continue
                um = round(menge * preis, 2)
                zeilen.append({"monat": "2026-%02d" % (m + 1), "produktlinie": li, "segment": s,
                               "menge_l": str(menge), "preis_eur_l": _zahl(preis), "umsatz_eur": _zahl(um),
                               "db_eur": _zahl(round(um - menge * kosten_l, 2))})
    zeilen.sort(key=lambda z: (z["monat"], LINIEN.index(z["produktlinie"]), z["segment"]))
    return zeilen


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------

FELDER = {
    "kunden.csv": ["id", "name", "segment", "land", "sprache", "ansprechpartner_name",
                   "ansprechpartner_rolle", "ansprechpartner_email", "key_account", "ist_haendler",
                   "beliefert_endkunden", "status"],
    "produkte.csv": ["id", "name", "schaumart", "brandklassen", "einsatzbereiche", "basis", "produktlinie",
                     "fluorfrei_deklariert", "zumischrate_prozent", "nachfolger_id", "status",
                     "eingefuehrt_am", "ausgelaufen_am"],
    "lieferstellen.csv": ["lieferstelle_id", "kunde_id", "anlage", "anwendung", "aktuelles_produkt_id",
                          "fuellmenge_l", "letzte_lieferung", "datenaufnahme_am", "zumischrate_anlage",
                          "zumischrate_crm"],
    "auftraege.csv": ["auftrag_id", "position", "auftragsdatum", "lieferdatum", "kunde_id", "lieferstelle_id",
                      "produkt_id", "anwendung", "menge", "einheit", "menge_l", "preis_netto_je_einheit",
                      "waehrung", "nettobetrag", "vertriebsweg", "art", "quellsystem"],
    "preisliste_2025.csv": ["produkt_id", "gebinde", "preis_netto_eur", "gueltig_ab"],
    "preisliste_2026.csv": ["produkt_id", "gebinde", "preis_netto_eur", "gueltig_ab"],
    "reklamationen.csv": ["rekl_id", "eingang", "kunde_id", "produkt_id", "kategorie", "auto_beantwortet",
                          "tage_bis_antwort", "status"],
    "kontakte.csv": ["datum", "kunde_id", "kanal", "richtung", "bearbeitung", "betreff", "dokument"],
    "herstellkosten.csv": ["produkt_id", "jahr", "rohstoff_eur_l", "fertigung_eur_l"],
    "fracht.csv": ["auftrag_id", "versanddatum", "kunde_id", "versandart", "liter", "frachtkosten_eur"],
    "kurse.csv": ["monat", "waehrung", "ist_kurs_eur", "plankurs_eur"],
    "budget_2026.csv": ["monat", "produktlinie", "segment", "menge_l", "preis_eur_l", "umsatz_eur", "db_eur"],
}


def csv_bytes(felder: list, zeilen: list) -> bytes:
    puffer = io.StringIO()
    w = csv.DictWriter(puffer, fieldnames=felder, lineterminator="\n")
    w.writeheader()
    for z in zeilen:
        w.writerow(z)
    return ("﻿" + puffer.getvalue()).encode("utf-8")


def erzeuge() -> dict:
    """Alle Dateien als {Dateiname: Bytes}."""
    kunden, produkte, lieferungen = lade_quelle()
    auftraege = baue_auftraege(kunden, produkte, lieferungen)
    herstellkosten = baue_herstellkosten(produkte)
    fracht = baue_fracht(auftraege, kunden)
    tabellen = {
        "kunden.csv": baue_kunden(kunden),
        "produkte.csv": baue_produkte(produkte),
        "lieferstellen.csv": baue_lieferstellen(lieferungen, produkte),
        "auftraege.csv": auftraege,
        "preisliste_2025.csv": baue_preisliste(produkte, 2025),
        "preisliste_2026.csv": baue_preisliste(produkte, 2026),
        "reklamationen.csv": baue_reklamationen(auftraege),
        "kontakte.csv": baue_kontakte(),
        "herstellkosten.csv": herstellkosten,
        "fracht.csv": fracht,
        "kurse.csv": baue_kurse(),
        "budget_2026.csv": baue_budget(auftraege, kunden, produkte, herstellkosten, fracht),
    }
    dateien = {name: csv_bytes(FELDER[name], zeilen) for name, zeilen in tabellen.items()}
    dateien["kennzahlen.json"] = (json.dumps(baue_kennzahlen(), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    dateien["_akte_dokumente.txt"] = baue_akte_liste().encode("utf-8")
    return dateien


def schreibe(dateien: dict) -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    for name, inhalt in dateien.items():
        (ZIEL / name).write_bytes(inhalt)
        print("geschrieben: daten/%s (%d Bytes)" % (name, len(inhalt)))


def pruefe_bytes(dateien: dict) -> list:
    fehler = []
    for name, inhalt in dateien.items():
        pfad = ZIEL / name
        if not pfad.exists():
            fehler.append("fehlt: daten/%s" % name)
        elif pfad.read_bytes() != inhalt:
            fehler.append("weicht ab: daten/%s (neu erzeugen)" % name)
    return fehler


def schreibe_sollwerte(ziel: Path) -> None:
    ziel = ziel.resolve()
    try:
        ziel.relative_to(REPO)
        raise SystemExit("Sollwerte nie ins Teilnehmer-Repo schreiben: %s" % ziel)
    except ValueError:
        pass
    import pruefe_daten  # gleicher Ordner
    werte = pruefe_daten.sollwerte(ZIEL)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(json.dumps(werte, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Sollwerte geschrieben:", ziel)


def main(argv: list | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="nur vergleichen und Regeln prüfen")
    ap.add_argument("--sollwerte", metavar="PFAD", help="Sollwerte als JSON ausserhalb des Repos schreiben")
    args = ap.parse_args(argv)
    dateien = erzeuge()
    if args.sollwerte:
        schreibe_sollwerte(Path(args.sollwerte))
        return 0
    if args.check:
        fehler = pruefe_bytes(dateien)
        if erzeuge() != dateien:
            fehler.append("nicht deterministisch: zwei Läufe unterscheiden sich")
        import pruefe_daten  # gleicher Ordner
        fehler += pruefe_daten.pruefe_alles(ZIEL)
        for f in fehler:
            print("FEHLER:", f)
        print("--check: %s" % ("grün" if not fehler else "%d Fehler" % len(fehler)))
        return 1 if fehler else 0
    schreibe(dateien)
    return 0


if __name__ == "__main__":
    sys.exit(main())
