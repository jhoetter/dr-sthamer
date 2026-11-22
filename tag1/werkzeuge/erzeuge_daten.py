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
RUHEND_AB = date(2025, 10, 1)  # K-1029: keine Aufträge mehr ab Oktober 2025

GEBINDE_L = {"l": 1, "Kanister": 20, "Fass": 200, "IBC": 1000}
JAHRE = list(range(2021, 2028))

# Generierte Dateien, die es nicht mehr gibt (werden beim Schreiben entfernt)
ENTFALLEN = ["kontakte.csv", "_akte_dokumente.txt"]

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


def _quartal(d: date) -> int:
    return (d.month - 1) // 3 + 1


def lade_quelle() -> tuple[list, list, list]:
    kunden = json.loads((QUELLE / "kunden.json").read_text(encoding="utf-8"))
    produkte = json.loads((QUELLE / "produkte.json").read_text(encoding="utf-8"))
    lieferungen = json.loads((QUELLE / "lieferungen.json").read_text(encoding="utf-8"))
    return kunden, produkte, lieferungen


# --------------------------------------------------------------------------
# Feste Annahmen der Übungswelt
# --------------------------------------------------------------------------

# Artikelbezeichnungen in Tag 1 (wo die Quelle eine abweichende Bezeichnung führt).
PRODUKTNAME = {
    "P-108": "Mittelschaum MS-30", "P-112": "TrainFoam Plus 3%", "P-118": "PureGuard 3%",
    "P-201": "NordFoam Neo 3%", "P-202": "NordFoam Neo 6%", "P-203": "NordFoam Neo AR 3x3",
    "P-204": "NordFoam Neo Marine 3%", "P-205": "NordFoam Neo Aero 3%", "P-206": "Waldfuchs Netzwasser Plus",
    "P-207": "NordFoam Neo MS Mittelschaum",
}
# Anlagenbezeichnungen in Tag 1 (Schlüssel bleibt die Bezeichnung der Quelle).
ANLAGENNAME = {
    "L-00012": "Zusatzlager", "L-00019": "Probelieferung", "L-00028": "Pilotanlage Schacht 7",
    "L-00053": "Zusatzfahrzeug", "L-00067": "Probelieferung", "L-00073": "Zusatzfahrzeug",
    "L-00083": "Probelieferung", "L-00096": "Muster", "L-00100": "Muster", "L-00103": "Muster",
    "L-00145": "Probelieferung",
}

# Einführungskalender (die Quelle hat kein Einführungsdatum).
EINFUEHRUNG = {
    "P-101": "2009-04-01", "P-102": "2009-04-01", "P-103": "2011-09-01", "P-104": "2012-03-01",
    "P-105": "2013-05-01", "P-106": "2010-02-01", "P-107": "2014-06-01", "P-108": "2008-10-01",
    "P-113": "2012-01-15", "P-117": "2015-03-01", "P-120": "2016-02-01", "P-121": "2010-09-01",
    "P-110": "2012-05-01", "P-111": "2015-04-01", "P-112": "2019-03-01", "P-114": "2018-06-01",
    "P-115": "2019-02-01", "P-116": "2019-02-01", "P-118": "2020-04-01", "P-119": "2020-09-01",
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
RAHMENVERTRAG = {"K-1002", "K-1013", "K-1017", "K-1020", "K-1022"}

# Nachfüllbedarf (Liter je Jahr als Vielfaches der Füllmenge) und Lieferungen je Jahr nach Anwendung.
UMSCHLAG = {"stationaere_anlage": 0.30, "feuerwehrfahrzeug": 0.85, "lager_bestand": 1.0,
            "uebung_training": 2.6, "tragbarer_feuerloescher": 1.3, "fahrbarer_feuerloescher": 0.9}
FREQUENZ = {"stationaere_anlage": 1.8, "feuerwehrfahrzeug": 3.0, "lager_bestand": 5.0,
            "uebung_training": 7.0, "tragbarer_feuerloescher": 10.0, "fahrbarer_feuerloescher": 6.0}
HAENDLER_FAKTOR = 2.0      # Händlerlager drehen schneller
FRUEHES_ENDE_FAKTOR = 0.6  # Lieferstellen ohne Lieferung seit 2026: seltener Bedarf

# Entwicklung des Nachfüllgeschäfts je Vertriebsweg (Index auf das Mittel 2021-2023 der Rohwerte).
# Händler wachsen jedes Jahr, direktes Nachfüllgeschäft und Rahmenverträge bleiben stabil.
NACHFUELL_INDEX = {
    "Händler": {2021: 0.92, 2022: 0.99, 2023: 1.06, 2024: 1.13, 2025: 1.20, 2026: 1.40, 2027: 1.45},
    "direkt": {2021: 1.00, 2022: 1.02, 2023: 0.98, 2024: 1.01, 2025: 1.00, 2026: 0.98, 2027: 0.98},
    "Rahmenvertrag": {2021: 0.98, 2022: 1.00, 2023: 1.02, 2024: 1.03, 2025: 1.04, 2026: 1.05, 2027: 1.05},
}
SAISON = [0.086, 0.084, 0.092, 0.090, 0.092, 0.087, 0.075, 0.087, 0.078, 0.092, 0.068, 0.069]
NACHFUELL_FAKTOR_MAX = 5.0

# Erstbefüllungen neuer stationärer Anlagen (Projektgeschäft): Lieferzeile -> Datum der Erstbefüllung.
# Vorher wird die Anlage nicht beliefert, danach folgt das Nachfüllgeschäft. 2025 viele grosse Anlagen,
# 2026 nur eine kleine.
ERSTBEFUELLUNG = {
    "L-00002": "2021-05-17", "L-00080": "2021-09-20",
    "L-00033": "2022-03-14", "L-00137": "2022-06-20", "L-00065": "2022-10-10",
    "L-00027": "2023-02-13", "L-00138": "2023-04-17", "L-00028": "2023-06-05", "L-00143": "2023-09-04",
    "L-00015": "2024-02-05", "L-00091": "2024-04-08", "L-00007": "2024-04-15", "L-00147": "2024-05-06",
    "L-00078": "2024-09-16",
    "L-00070": "2025-02-10", "L-00141": "2025-03-17", "L-00142": "2025-05-12", "L-00079": "2025-06-16",
    "L-00008": "2025-09-22",
    "L-00021": "2026-05-11",
}

# Weitere Lieferzeilen mit Beginn im Zeitraum (neue Fahrzeuge, Lager) oder Artikelwechsel.
# ("start", Datum): erste Lieferung = Erstbefüllung mit der Füllmenge.
# ("wechsel", Datum, Vorgänger): vorher Vorgängerartikel an derselben Lieferstelle.
# ("einmal", "Muster"): genau eine Musterlieferung am Datum der letzten Lieferung.
VERLAUF = {
    "L-00006": ("wechsel", "2022-05-02", "P-113"), "L-00025": ("wechsel", "2023-03-06", "P-113"),
    "L-00041": ("wechsel", "2021-09-13", "P-113"), "L-00048": ("wechsel", "2022-10-04", "P-113"),
    "L-00054": ("wechsel", "2021-06-07", "P-113"), "L-00068": ("wechsel", "2024-02-05", "P-113"),
    "L-00074": ("wechsel", "2023-09-11", "P-113"), "L-00129": ("wechsel", "2024-06-03", "P-113"),
    "L-00132": ("wechsel", "2025-01-13", "P-113"),
    "L-00039": ("wechsel", "2022-04-04", "P-120"), "L-00040": ("wechsel", "2022-04-04", "P-120"),
    "L-00035": ("wechsel", "2023-05-08", "P-120"),
    "L-00044": ("start", "2022-06-01"), "L-00047": ("start", "2023-04-03"),
    "L-00061": ("start", "2021-03-01"), "L-00058": ("start", "2023-02-01"),
    "L-00110": ("start", "2021-05-03"), "L-00114": ("start", "2022-03-01"),
    "L-00108": ("start", "2022-01-10"), "L-00024": ("start", "2022-09-05"),
    "L-00038": ("start", "2024-03-04"), "L-00148": ("start", "2023-01-09"),
    "L-00121": ("start", "2022-04-04"), "L-00123": ("start", "2023-03-01"), "L-00125": ("start", "2023-03-01"),
    "L-00012": ("start", "2025-04-07"), "L-00053": ("start", "2022-03-07"),
    "L-00073": ("start", "2025-03-03"), "L-00115": ("start", "2021-10-04"),
    "L-00019": ("einmal", "Muster"), "L-00067": ("einmal", "Muster"), "L-00083": ("einmal", "Muster"),
    "L-00145": ("einmal", "Muster"), "L-00096": ("einmal", "Muster"), "L-00100": ("einmal", "Muster"),
    "L-00103": ("einmal", "Muster"),
}

# Notfalleinsätze (Ausreisser): Lieferzeile, Lieferdatum, IBC
NOTFALL = [("L-00020", "2022-08-16", 18), ("L-00063", "2024-03-11", 20), ("L-00141", "2026-09-22", 24)]


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
# Stammtabellen
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
            "id": p["id"], "name": PRODUKTNAME.get(p["id"], p["name"]), "schaumart": p["schaumart"],
            "einsatzbereiche": ";".join(p["einsatzbereiche"]), "status": p["status"],
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


def baue_lieferstellen(lieferungen: list, auftraege: list) -> list:
    _, zeile_ls = lieferstellen_index(lieferungen)
    gruppen = {}
    for l in lieferungen:
        gruppen.setdefault(zeile_ls[l["id"]], []).append(l)
    erstbef = {}
    for z in auftraege:
        if z["auftragsart"] == "Erstbefüllung" and z["art"] == "Lieferung":
            ls = z["lieferstelle_id"]
            erstbef[ls] = min(erstbef.get(ls, "9999"), z["lieferdatum"])
    zeilen = []
    for ls_id in sorted(gruppen):
        g = gruppen[ls_id]
        aktuell = max(g, key=lambda l: (l["letzte_lieferung"], -g.index(l)))
        zeilen.append({
            "lieferstelle_id": ls_id, "kunde_id": g[0]["kunde_id"],
            "anlage": ANLAGENNAME.get(g[0]["id"], g[0]["anlage"]),
            "anwendung": g[0]["anwendung"], "aktuelles_produkt_id": aktuell["produkt_id"],
            "fuellmenge_l": str(sum(x["menge_l"] for x in g)),
            "letzte_lieferung": max(x["letzte_lieferung"] for x in g),
            "erstbefuellung_am": erstbef.get(ls_id, ""),
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


# --------------------------------------------------------------------------
# Aufträge
# --------------------------------------------------------------------------


def _menge_einheit(pid: str, liter: float, anwendung: str) -> tuple[str, int]:
    """Liter -> (Einheit, Anzahl) nach Gebindelogik."""
    if liter >= 5000 and pid in LOSE_WARE and anwendung == "stationaere_anlage":
        return "l", max(500, int(round(liter / 500.0)) * 500)
    if liter >= 1000:
        return "IBC", max(1, int(round(liter / 1000.0)))
    if liter >= 200:
        return "Fass", max(1, int(round(liter / 200.0)))
    return "Kanister", max(1, int(round(liter / 20.0)))


def standardweg(k: dict) -> str:
    if k["ist_haendler"]:
        return "Händler"
    if k["id"] in RAHMENVERTRAG:
        return "Rahmenvertrag"
    return "direkt"


def _ereignisse_zeile(l: dict) -> list:
    """Rohe Lieferereignisse einer Lieferzeile: dict(datum, pid, liter, art, auftragsart)."""
    anw = l["anwendung"]
    ende = _d(l["letzte_lieferung"])
    verlauf = VERLAUF.get(l["id"])
    if verlauf and verlauf[0] == "einmal":
        return [{"datum": ende, "pid": l["produkt_id"], "liter": float(l["menge_l"]), "art": "Muster",
                 "auftragsart": "Muster"}]

    start = START
    wechsel = None
    vorgaenger = None
    erstbef = None
    if l["id"] in ERSTBEFUELLUNG:
        erstbef = _d(ERSTBEFUELLUNG[l["id"]])
    elif verlauf and verlauf[0] == "start":
        erstbef = _d(verlauf[1])
    elif verlauf and verlauf[0] == "wechsel":
        wechsel = _d(verlauf[1])
        vorgaenger = verlauf[2]
    if erstbef is not None:
        start = erstbef + timedelta(days=45)

    ereignisse = []
    frequenz = FREQUENZ[anw] * (0.8 + 0.4 * _u("f", l["id"]))
    intervall = 365.0 / frequenz
    jahresmenge = l["menge_l"] * UMSCHLAG[anw] * (0.8 + 0.4 * _u("m", l["id"]))
    if l["kunde_id"] in ("K-1023", "K-1024"):
        jahresmenge *= HAENDLER_FAKTOR
    if ende < date(2026, 1, 1):
        jahresmenge *= FRUEHES_ENDE_FAKTOR

    d = ende
    i = 0
    while d >= start or i == 0:
        pid = l["produkt_id"]
        if wechsel is not None and d < wechsel:
            pid = vorgaenger
        liter = jahresmenge / frequenz * (0.6 + 0.8 * _u("q", l["id"], i))
        frueh = max(start, wechsel if (wechsel is not None and pid != vorgaenger) else START,
                    _d(EINFUEHRUNG[pid]))
        ereignisse.append({"datum": d, "pid": pid, "liter": liter, "art": "Lieferung",
                           "auftragsart": "Nachfüllung", "frueh": frueh})
        i += 1
        schritt = intervall * (0.55 + 0.9 * _u("t", l["id"], i))
        d = d - timedelta(days=max(7, int(round(schritt))))
    if erstbef is not None:
        ereignisse.append({"datum": erstbef, "pid": l["produkt_id"], "liter": float(l["menge_l"]),
                           "art": "Lieferung", "auftragsart": "Erstbefüllung"})
    return ereignisse


def _nachfuell_faktoren(roh: list, feld: str = "liter", basis_von: dict | None = None,
                        grenze: float = 1e9) -> tuple[dict, dict]:
    """Faktor je (Vertriebsweg, Jahr, Quartal), damit das Nachfüllgeschäft dem Index folgt; dazu die Basis."""
    summe = {}
    for e in roh:
        if e["auftragsart"] != "Nachfüllung":
            continue
        s = (e["weg"], e["datum"].year, _quartal(e["datum"]))
        summe[s] = summe.get(s, 0.0) + e.get(feld, e["liter"])
    anteil_q = [sum(SAISON[3 * (q - 1): 3 * q]) for q in (1, 2, 3, 4)]
    faktoren = {}
    basen = {}
    for weg, index in NACHFUELL_INDEX.items():
        basis = sum(summe.get((weg, j, q), 0.0) for j in (2021, 2022, 2023) for q in (1, 2, 3, 4)) / 3.0
        if basis_von is not None:
            basis = basis_von[weg]
        basen[weg] = basis
        for j in JAHRE:
            for q in (1, 2, 3, 4):
                ist = summe.get((weg, j, q), 0.0)
                if ist <= 0:
                    continue
                anteil = anteil_q[q - 1]
                if j == 2027 and q == 1:
                    anteil = SAISON[0] + SAISON[1]
                faktoren[(weg, j, q)] = min(grenze, basis * index[j] * anteil / ist)
    return faktoren, basen


def baue_auftraege(kunden: list, produkte: list, lieferungen: list) -> list:
    kunde = {k["id"]: k for k in kunden}
    _, zeile_ls = lieferstellen_index(lieferungen)

    # 1. Rohe Ereignisse mit Vertriebsweg
    roh = []
    for l in lieferungen:
        k = kunde[l["kunde_id"]]
        for e in _ereignisse_zeile(l):
            if e["datum"] < START:
                continue
            if l["kunde_id"] == "K-1029" and e["datum"] >= RUHEND_AB:
                continue
            if e["datum"] < _d(EINFUEHRUNG[e["pid"]]):
                continue
            if e["art"] == "Muster":
                weg = "direkt"
            elif e["auftragsart"] == "Erstbefüllung" and not k["ist_haendler"]:
                weg = "direkt"  # Projektgeschäft läuft immer direkt, auch bei Rahmenvertragskunden
            else:
                weg = standardweg(k)
            e = dict(e)
            e.update({"weg": weg, "zeile": l})
            roh.append(e)

    # Erstbefüllung nur, wenn die Lieferstelle vorher nichts bekommen hat (sonst: neuer Artikel an einer
    # bestehenden Lieferstelle = Nachfüllung)
    frueheste = {}
    for e in roh:
        ls = zeile_ls[e["zeile"]["id"]]
        frueheste[ls] = min(frueheste.get(ls, e["datum"]), e["datum"])
    erst_ls = set()
    for e in sorted(roh, key=lambda e: (e["datum"], e["zeile"]["id"])):
        if e["auftragsart"] != "Erstbefüllung":
            continue
        ls = zeile_ls[e["zeile"]["id"]]
        if ls in erst_ls or e["datum"] > frueheste[ls]:
            e["auftragsart"] = "Nachfüllung"
            e["frueh"] = e["datum"]
            e["weg"] = standardweg(kunde[e["zeile"]["kunde_id"]])
        else:
            erst_ls.add(ls)

    # 2. Nachfüllgeschäft kalibrieren (Händler wachsen, direkt und Rahmenvertrag stabil)
    faktoren, basen = _nachfuell_faktoren(roh, grenze=NACHFUELL_FAKTOR_MAX)
    # Mehr Bedarf heißt mehr Lieferungen gleicher Größe: Faktor >= 1 -> zusätzliche Lieferungen in den
    # Wochen davor; Faktor < 1 -> kleinere Lieferung. So bleiben Gebinde und Liefergrößen je Lieferstelle gleich.
    erweitert = []
    for e in roh:
        if e["auftragsart"] != "Nachfüllung":
            erweitert.append(e)
            continue
        f = faktoren.get((e["weg"], e["datum"].year, _quartal(e["datum"])), 1.0)
        if f < 1.0:
            e = dict(e)
            e["liter_skaliert"] = e["liter"] * f
            erweitert.append(e)
            continue
        anzahl = int(f) + (1 if _u("nf", e["zeile"]["id"], e["datum"]) < f - int(f) else 0)
        d = e["datum"]
        for n in range(max(1, anzahl)):
            if n > 0:
                d = d - timedelta(days=9 + _h("nfd", e["zeile"]["id"], e["datum"], n) % 24)
                if d < e["frueh"]:
                    break
            k = dict(e)
            k.update({"datum": d, "liter_skaliert": e["liter"]})
            erweitert.append(k)
    # Feinabgleich nach dem Verschieben der zusätzlichen Lieferungen (nahe 1)
    fein, _ = _nachfuell_faktoren(erweitert, "liter_skaliert", basen, grenze=1.5)
    for e in erweitert:
        if e["auftragsart"] == "Nachfüllung":
            e["liter_skaliert"] *= fein.get((e["weg"], e["datum"].year, _quartal(e["datum"])), 1.0)
    roh = erweitert
    positionen = []

    def neue_position(l, lieferdatum, pid, menge, einheit, art, auftragsart, weg, auftragsdatum):
        k = kunde[l["kunde_id"]]
        jahr = lieferdatum.year
        preis_eur = listenpreis(pid, einheit, jahr) if art != "Muster" else 0.0
        if weg == "Händler":
            preis_eur *= 0.82
        elif weg == "Rahmenvertrag":
            preis_eur *= 0.92
        elif weg == "Notfallservice":
            preis_eur *= 1.35
        elif k["key_account"]:
            preis_eur *= 0.95
        if jahr == 2026 and art == "Lieferung":
            preis_eur *= preisschutz_2026(weg, auftragsdatum)
        waehrung = WAEHRUNG.get(k["id"], "EUR")
        preis = preis_eur
        if waehrung != "EUR":
            preis = preis_eur / KONZERNKURSE[str(jahr)][waehrung]
        positionen.append({
            "auftragsdatum": auftragsdatum, "lieferdatum": lieferdatum, "kunde_id": l["kunde_id"],
            "lieferstelle_id": zeile_ls[l["id"]], "produkt_id": pid, "anwendung": l["anwendung"],
            "menge": menge, "einheit": einheit, "preis": round(preis, 2), "waehrung": waehrung,
            "vertriebsweg": weg, "art": art, "auftragsart": auftragsart, "zeile": l["id"],
        })

    for e in roh:
        l = e["zeile"]
        liter = e.get("liter_skaliert", e["liter"])
        if e["art"] == "Muster":
            einheit, menge = "Kanister", max(1, int(round(liter / 20)))
        elif e["auftragsart"] == "Erstbefüllung" and l["anwendung"] == "stationaere_anlage":
            if e["pid"] in LOSE_WARE:
                einheit, menge = "l", int(liter)
            else:
                einheit, menge = "IBC", max(1, int(round(liter / 1000.0)))
        else:
            # Gebinde nach dem üblichen Bedarf der Lieferstelle (ungeskaliert), Anzahl nach dem Bedarf
            einheit, _ = _menge_einheit(e["pid"], e["liter"], l["anwendung"])
            if einheit == "l":
                menge = max(500, int(round(liter / 500.0)) * 500)
            else:
                menge = max(1, int(round(liter / GEBINDE_L[einheit])))
        vorlauf = 2 + _h("v", l["id"], e["datum"]) % 11
        if e["auftragsart"] == "Erstbefüllung":
            vorlauf = 21 + _h("ve", l["id"]) % 35  # Projekte werden früher bestellt
        auftragsdatum = max(START, e["datum"] - timedelta(days=vorlauf))
        neue_position(l, e["datum"], e["pid"], menge, einheit, e["art"], e["auftragsart"], e["weg"],
                      auftragsdatum)

    zeile_von = {l["id"]: l for l in lieferungen}
    for (zid, datum, ibc) in NOTFALL:
        l = zeile_von[zid]
        lieferdatum = _d(datum)
        neue_position(l, lieferdatum, l["produkt_id"], ibc, "IBC", "Lieferung", "Notfall", "Notfallservice",
                      lieferdatum - timedelta(days=1))

    # Gutschriften und Retouren (negativ), mit Auftragsart der ursprünglichen Lieferung
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
    positionen.extend(gutschriften)

    # Auftragsnummern: je Kunde, Auftragsdatum, Vertriebsweg, Art und Auftragsart ein Auftrag
    positionen.sort(key=lambda p: (p["auftragsdatum"], p["kunde_id"], p["vertriebsweg"], p["art"],
                                   p["auftragsart"], p["lieferstelle_id"], p["produkt_id"], p["lieferdatum"]))
    zaehler = {}
    auftrag_von = {}
    pos_zaehler = {}
    zeilen = []
    for p in positionen:
        schluessel = (p["auftragsdatum"], p["kunde_id"], p["vertriebsweg"], p["art"], p["auftragsart"])
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
            "vertriebsweg": p["vertriebsweg"], "auftragsart": p["auftragsart"], "art": p["art"],
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
# Reklamationen
# --------------------------------------------------------------------------

KATEGORIEN = ["Lieferverzug", "Lieferung/Menge", "Gebinde/Verpackung", "Rechnung", "Dokumentation",
              "Beschädigte Ware"]
REKLAMATIONEN_ANZAHL = 48


def baue_reklamationen(auftraege: list) -> list:
    kandidaten = []
    gesehen = set()
    for z in auftraege:
        if z["art"] != "Lieferung" or z["lieferdatum"] < "2023-12-01":
            continue
        schluessel = (z["auftrag_id"], z["position"])
        if schluessel in gesehen:
            continue
        gesehen.add(schluessel)
        kandidaten.append(z)
    kandidaten.sort(key=lambda z: _h("rk", z["auftrag_id"], z["position"]))
    faelle = []
    for z in kandidaten:
        if len(faelle) >= REKLAMATIONEN_ANZAHL:
            break
        eingang = _d(z["lieferdatum"]) + timedelta(days=3 + _h("rke", z["auftrag_id"]) % 35)
        if eingang < date(2024, 1, 2) or eingang > date(2027, 2, 26):
            continue
        kat = KATEGORIEN[_h("rkk", z["auftrag_id"]) % len(KATEGORIEN)]
        if z["vertriebsweg"] == "Notfallservice":
            kat = "Lieferverzug"
        tage = 1 + _h("rkt", z["auftrag_id"]) % 9
        if eingang >= date(2027, 2, 1):
            status = "offen"
        elif _u("rks2", z["auftrag_id"]) < 0.15:
            status = "abgeschlossen (Kulanz)"
        elif _u("rks", z["auftrag_id"]) < 0.12:
            status = "abgelehnt"
        else:
            status = "abgeschlossen"
        faelle.append((eingang.isoformat(), z["kunde_id"], z["produkt_id"], kat, tage, status))
    faelle.sort(key=lambda f: (f[0], f[1], f[2]))
    zeilen = []
    zaehler = {}
    for (eingang, kid, pid, kat, tage, status) in faelle:
        jahr = eingang[:4]
        zaehler[jahr] = zaehler.get(jahr, 0) + 1
        zeilen.append({
            "rekl_id": "R-%s-%03d" % (jahr, zaehler[jahr]), "eingang": eingang, "kunde_id": kid,
            "produkt_id": pid, "kategorie": kat, "tage_bis_antwort": str(tage), "status": status,
        })
    return zeilen


# --------------------------------------------------------------------------
# Finanzdaten (Drill 2): Herstellkosten, Fracht, Kurse, Budget 2026
# --------------------------------------------------------------------------

# Herstellkosten je Liter: Rohstoff als Anteil am Listenpreis 2026 je Liter, Fertigung je Schaumart.
HK_ROHSTOFF_ANTEIL = {"Schwerschaum": 0.36, "Mittelschaum": 0.40, "Übungsschaum": 0.50, "Netzwasser": 0.30,
                      "Retardant": 0.52, "CAFS": 0.32}
HK_FERTIGUNG_L = {"Schwerschaum": 0.48, "Mittelschaum": 0.50, "Übungsschaum": 0.42, "Netzwasser": 0.46,
                  "Retardant": 0.40, "CAFS": 0.55}
HK_INDEX = {2021: 0.86, 2022: 0.97, 2023: 1.03, 2024: 1.00, 2025: 0.98, 2026: 1.0, 2027: 1.01}

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

# Budget 2026 (aufgestellt im Herbst 2025 aus dem Ist 2025): Wachstum je Vertriebsweg; das Projektgeschäft
# (Erstbefüllungen) ist wie 2025 eingeplant. Nettopreise wie Ist 2025 (Preiserhöhung nicht eingeplant),
# Kosten = Herstellkosten 2026 beim Produktmix 2025 + Fracht je Liter 2025 der Zelle.
BUDGET_WACHSTUM = {"Händler": 1.10, "direkt": 1.04, "Rahmenvertrag": 1.03}
WEGE = ["direkt", "Händler", "Rahmenvertrag"]


def baue_herstellkosten(produkte: list) -> list:
    zeilen = []
    for p in sorted(produkte, key=lambda x: x["id"]):
        art = p["schaumart"]
        streuung = 0.92 + 0.16 * _u("hk", p["id"])
        roh26 = PREIS_L_2026[p["id"]] * HK_ROHSTOFF_ANTEIL[art] * streuung
        fert26 = HK_FERTIGUNG_L[art] * (0.95 + 0.10 * _u("hkf", p["id"]))
        for j in JAHRE:
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


def baue_budget(auftraege: list, kunden: list, herstellkosten: list, fracht: list) -> list:
    """Budget 2026 je Monat x Segment x Vertriebsweg, abgeleitet aus dem Ist 2025."""
    segment = {k["id"]: k["segment"] for k in kunden}
    hk = _hk_je_l(herstellkosten)
    pos = _eindeutig(auftraege)
    weg_auftrag = {z["auftrag_id"]: z["vertriebsweg"] for z in pos}
    # Fracht 2025 je Liter und Zelle (ohne Express)
    fr_zelle = {}
    for f in fracht:
        if f["versanddatum"][:4] == "2025" and f["versandart"] != "Express":
            c = (segment[f["kunde_id"]], weg_auftrag[f["auftrag_id"]])
            b, l = fr_zelle.get(c, (0.0, 0))
            fr_zelle[c] = (b + float(f["frachtkosten_eur"]), l + int(f["liter"]))
    # Ist 2025 je Zelle: Liter, Umsatz EUR (Konzernkurs 2025), Liter je Produkt
    liter = {}
    umsatz = {}
    mix = {}
    for z in pos:
        if z["lieferdatum"][:4] != "2025" or z["art"] == "Muster" or z["vertriebsweg"] == "Notfallservice":
            continue
        c = (segment[z["kunde_id"]], z["vertriebsweg"])
        lt = _liter_z(z)
        kurs = 1.0 if z["waehrung"] == "EUR" else KONZERNKURSE["2025"][z["waehrung"]]
        liter[c] = liter.get(c, 0) + lt
        umsatz[c] = umsatz.get(c, 0.0) + float(z["nettobetrag"]) * kurs
        mix.setdefault(c, {})
        mix[c][z["produkt_id"]] = mix[c].get(z["produkt_id"], 0) + lt
    zeilen = []
    for c in sorted(liter):
        if liter[c] <= 0:
            continue
        s, weg = c
        jahr_l = liter[c] * BUDGET_WACHSTUM[weg]
        preis = round(umsatz[c] / liter[c], 2)
        pm = mix[c]
        pl = sum(v for v in pm.values() if v > 0)
        b, l = fr_zelle.get(c, (0.0, 0))
        fracht_l = b / l if l else 0.15
        kosten_l = sum(hk[(pid, 2026)] * v for pid, v in pm.items() if v > 0) / pl + fracht_l
        for m in range(12):
            menge = int(round(jahr_l * SAISON[m] / 10.0)) * 10
            if menge <= 0:
                continue
            um = round(menge * preis, 2)
            zeilen.append({"monat": "2026-%02d" % (m + 1), "segment": s, "vertriebsweg": weg,
                           "menge_l": str(menge), "preis_eur_l": _zahl(preis), "umsatz_eur": _zahl(um),
                           "db_eur": _zahl(round(um - menge * kosten_l, 2))})
    zeilen.sort(key=lambda z: (z["monat"], z["segment"], WEGE.index(z["vertriebsweg"])))
    return zeilen


# --------------------------------------------------------------------------
# Kennzahlen und Ziele
# --------------------------------------------------------------------------


def baue_kennzahlen(budget: list) -> dict:
    plan_umsatz = sum(float(b["umsatz_eur"]) for b in budget)
    plan_db = sum(float(b["db_eur"]) for b in budget)
    plan_liter = sum(int(b["menge_l"]) for b in budget)
    return {
        "stichtag": STICHTAG.isoformat(),
        "heute": HEUTE.isoformat(),
        "waehrung_konzern": "EUR",
        "konzernkurse": {"hinweis": "1 Einheit Fremdwährung = x EUR, Jahresdurchschnitt; 2027 = Kurs 2026",
                         "kurse": KONZERNKURSE},
        "ziele": {
            "hinweis": "Ziele der Geschäftsführung für 2026 = Budget 2026 (budget_2026.csv), zum Plankurs, "
                       "ohne Notfallservice; für 2027 noch nicht beschlossen",
            "2026": {"nettoumsatz_eur": round(plan_umsatz, 2), "absatz_l": plan_liter,
                     "deckungsbeitrag_eur": round(plan_db, 2),
                     "db_marge": round(plan_db / plan_umsatz, 4)},
        },
        "definitionen": {
            "bereinigung": {
                "doppelimporte": "gleiche auftrag_id und position nur einmal zählen",
                "jahr": "nach Lieferdatum (Kalenderjahr); Jan.-Feb. 2027 ist ein Teiljahr",
            },
            "umrechnung_gebinde": {"IBC": 1000, "Fass": 200, "Kanister": 20, "l": 1},
            "absatz_l": {
                "formel": "Summe Liter aller Positionen, netto (Gutschriften und Retouren mit ihren negativen "
                          "Mengen abziehen), ohne Muster",
                "liter": "menge_l; fehlt es, menge x Gebindegröße (umrechnung_gebinde)",
            },
            "nettoumsatz": "Summe nettobetrag aller Positionen (Lieferungen, Gutschriften und Retouren negativ, "
                           "Muster 0), Fremdwährung zum Konzernkurs des Lieferjahres in EUR",
            "wachstum": {
                "formel": "Wert 2026 / Wert 2025 - 1, für Absatz (Liter) oder Nettoumsatz (EUR)",
                "hinweis": "nur ganze Jahre vergleichen; Teiljahr 2027 nie gegen ganze Jahre stellen",
            },
            "auftragsart": {
                "Nachfüllung": "wiederkehrender Bedarf einer bestehenden Lieferstelle (Ersatz nach Einsatz, "
                               "Übung, Ablauf, Lagerumschlag)",
                "Erstbefüllung": "erste Befüllung einer neuen Anlage, eines neuen Fahrzeugs oder Lagers "
                                 "(einmaliges Projektgeschäft)",
                "Notfall": "Lieferung des Notfallservice nach einem Einsatz (nicht planbar, nicht budgetiert)",
                "Muster": "Musterlieferung, 0 EUR, zählt nicht zum Absatz",
            },
            "nachfuell_anteil": {
                "formel": "Absatz (Liter) mit auftragsart = 'Nachfüllung' / gesamter Absatz (Liter) im Kalenderjahr",
                "projektanteil": "Absatz mit auftragsart = 'Erstbefüllung' / gesamter Absatz",
                "hinweis": "Gutschriften und Retouren zählen zu der Auftragsart der ursprünglichen Lieferung",
            },
            "top5_anteil": {
                "formel": "Nettoumsatz der fünf umsatzstärksten Kunden / gesamter Nettoumsatz im Kalenderjahr",
                "kunde": "Kunde nach kunde_id (Händler zählen als ein Kunde, ihre Endkunden nicht einzeln)",
            },
            "aktiver_kunde": "mindestens ein Auftrag (art = 'Lieferung') in den 24 Monaten vor dem Stichtag",
            "kundenstatus": {
                "grundlage": "Lieferdatum der letzten Lieferung (art = 'Lieferung') je Kunde, gemessen am Stichtag",
                "aktiv": "letzte Lieferung höchstens 12 Monate vor dem Stichtag (ab 01.03.2026)",
                "ruhend": "letzte Lieferung 12 bis 24 Monate vor dem Stichtag (01.03.2025 bis 28.02.2026)",
                "verloren": "letzte Lieferung mehr als 24 Monate vor dem Stichtag (vor 01.03.2025) oder nie",
                "hinweis": "aktiv + ruhend = aktiver Kunde (24 Monate); das Feld status im Kundenstamm ist "
                           "etwas anderes",
            },
            "deckungsbeitrag": {
                "formel": "Deckungsbeitrag = Nettoumsatz - Herstellkosten - Fracht; DB-Marge = Deckungsbeitrag / Nettoumsatz",
                "nettoumsatz": "Summe nettobetrag aller Positionen (Lieferungen, Gutschriften und Retouren negativ, "
                               "Muster 0) in EUR, ohne Doppelimporte, Jahr nach Lieferdatum",
                "herstellkosten": "Liter x (rohstoff_eur_l + fertigung_eur_l) aus herstellkosten.csv für Produkt und "
                                  "Lieferjahr; für Lieferungen und Muster, Retouren mindern (Ware kommt zurück); "
                                  "Gutschriften ohne Herstellkosten (Ware bleibt beim Kunden)",
                "fracht": "fracht.csv je Auftrag; auf die Positionen des Auftrags nach Litern verteilt, "
                          "Jahr nach Lieferdatum der Position",
                "produktgruppe": "Schaumart aus produkte.csv",
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
                "zellen": "Segment x Vertriebsweg, Kalenderjahr 2026",
                "ist": "netto Liter wie absatz_l; Umsatz und Kosten wie deckungsbeitrag; "
                       "Notfallservice nicht in den Zellen, sondern als eigener Balken (nicht budgetiert)",
                "reihenfolge": "Menge, Mix, Preis, (beim Deckungsbeitrag) Kosten, Fremdwährung, Notfallservice",
                "mengeneffekt": "(Ist-Liter gesamt - Plan-Liter gesamt) x Plan-Durchschnitt je Liter",
                "mixeffekt": "Summe je Zelle (Ist-Liter x Plan-Wert je Liter) - Ist-Liter gesamt x Plan-Durchschnitt je Liter",
                "preiseffekt": "Summe je Zelle (Ist-Umsatz zum Plankurs - Ist-Liter x Plan-Preis je Liter)",
                "kosteneffekt": "nur Deckungsbeitrag: Summe je Zelle (Ist-Liter x Plan-Kosten je Liter - Ist-Kosten); "
                                "Plan-Kosten je Liter = Plan-Preis - Plan-DB je Liter",
                "fremdwaehrungseffekt": "wie umrechnung_fremdwaehrung, ohne Notfallservice",
                "wert_je_liter": "Umsatzbrücke: Umsatz je Liter; DB-Brücke: Deckungsbeitrag je Liter",
            },
        },
        "ampel_wachstum": {
            "grundlage": "Veränderung des Nettoumsatzes 2026 gegen 2025 je Gruppe (Konzernkurs), aus Summen gerechnet",
            "wachstum": "> +0.05",
            "stabil": "-0.05 bis +0.05 (beide Grenzen eingeschlossen)",
            "rueckgang": "< -0.05",
            "luecke": "weniger als 20 Positionen 2026 oder 2025: keine Ampel, als Lücke zeigen",
        },
    }


# --------------------------------------------------------------------------
# Ausgabe
# --------------------------------------------------------------------------

FELDER = {
    "kunden.csv": ["id", "name", "segment", "land", "sprache", "ansprechpartner_name",
                   "ansprechpartner_rolle", "ansprechpartner_email", "key_account", "ist_haendler",
                   "beliefert_endkunden", "status"],
    "produkte.csv": ["id", "name", "schaumart", "einsatzbereiche", "status", "eingefuehrt_am", "ausgelaufen_am"],
    "lieferstellen.csv": ["lieferstelle_id", "kunde_id", "anlage", "anwendung", "aktuelles_produkt_id",
                          "fuellmenge_l", "letzte_lieferung", "erstbefuellung_am"],
    "auftraege.csv": ["auftrag_id", "position", "auftragsdatum", "lieferdatum", "kunde_id", "lieferstelle_id",
                      "produkt_id", "anwendung", "menge", "einheit", "menge_l", "preis_netto_je_einheit",
                      "waehrung", "nettobetrag", "vertriebsweg", "auftragsart", "art", "quellsystem"],
    "preisliste_2025.csv": ["produkt_id", "gebinde", "preis_netto_eur", "gueltig_ab"],
    "preisliste_2026.csv": ["produkt_id", "gebinde", "preis_netto_eur", "gueltig_ab"],
    "reklamationen.csv": ["rekl_id", "eingang", "kunde_id", "produkt_id", "kategorie", "tage_bis_antwort", "status"],
    "herstellkosten.csv": ["produkt_id", "jahr", "rohstoff_eur_l", "fertigung_eur_l"],
    "fracht.csv": ["auftrag_id", "versanddatum", "kunde_id", "versandart", "liter", "frachtkosten_eur"],
    "kurse.csv": ["monat", "waehrung", "ist_kurs_eur", "plankurs_eur"],
    "budget_2026.csv": ["monat", "segment", "vertriebsweg", "menge_l", "preis_eur_l", "umsatz_eur", "db_eur"],
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
    budget = baue_budget(auftraege, kunden, herstellkosten, fracht)
    tabellen = {
        "kunden.csv": baue_kunden(kunden),
        "produkte.csv": baue_produkte(produkte),
        "lieferstellen.csv": baue_lieferstellen(lieferungen, auftraege),
        "auftraege.csv": auftraege,
        "preisliste_2025.csv": baue_preisliste(produkte, 2025),
        "preisliste_2026.csv": baue_preisliste(produkte, 2026),
        "reklamationen.csv": baue_reklamationen(auftraege),
        "herstellkosten.csv": herstellkosten,
        "fracht.csv": fracht,
        "kurse.csv": baue_kurse(),
        "budget_2026.csv": budget,
    }
    dateien = {name: csv_bytes(FELDER[name], zeilen) for name, zeilen in tabellen.items()}
    dateien["kennzahlen.json"] = (json.dumps(baue_kennzahlen(budget), ensure_ascii=False, indent=2)
                                  + "\n").encode("utf-8")
    return dateien


def schreibe(dateien: dict) -> None:
    ZIEL.mkdir(parents=True, exist_ok=True)
    for name, inhalt in dateien.items():
        (ZIEL / name).write_bytes(inhalt)
        print("geschrieben: daten/%s (%d Bytes)" % (name, len(inhalt)))
    for name in ENTFALLEN:
        if (ZIEL / name).exists():
            (ZIEL / name).unlink()
            print("entfernt: daten/%s" % name)


def pruefe_bytes(dateien: dict) -> list:
    fehler = []
    for name, inhalt in dateien.items():
        pfad = ZIEL / name
        if not pfad.exists():
            fehler.append("fehlt: daten/%s" % name)
        elif pfad.read_bytes() != inhalt:
            fehler.append("weicht ab: daten/%s (neu erzeugen)" % name)
    for name in ENTFALLEN:
        if (ZIEL / name).exists():
            fehler.append("entfallen, liegt noch da: daten/%s (neu erzeugen)" % name)
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
