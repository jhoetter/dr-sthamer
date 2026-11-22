#!/usr/bin/env python3
"""Konsistenzprüfungen für die Daten und Texte von Tag 1 (Regeln 1-10, 11-13 Finanzen, 14 Geschäftsbefunde, 15 Themen).

Nur Standardbibliothek, Python >= 3.9. Bewusst kein test_*.py, damit die
Prüfszenarien von Tag 2 nichts davon einsammeln.

Aufruf:  python werkzeuge/pruefe_daten.py
"""
from __future__ import annotations

import base64
import csv
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

WERKZEUGE = Path(__file__).resolve().parent
TAG1 = WERKZEUGE.parent
REPO = TAG1.parent
QUELLE = REPO / "data"
DATEN = TAG1 / "daten"

STICHTAG = "2027-02-28"
NOTIZBUCH_ENDE = "2027-02-26"
GEBINDE_L = {"l": 1, "Kanister": 20, "Fass": 200, "IBC": 1000}
JAHRE = [str(j) for j in range(2021, 2028)]
WEGE = ["direkt", "Händler", "Rahmenvertrag", "Notfallservice"]
AUFTRAGSARTEN = ["Nachfüllung", "Erstbefüllung", "Notfall", "Muster"]

# Spoiler-Schutz 2.4
FALLTRAEGER_GESPERRT = ["K-1007", "K-1010", "K-1011", "K-1014", "K-1015", "K-1017", "K-1021", "K-1023",
                        "K-1026", "K-1027", "K-1001", "K-1030", "K-1008", "K-1009", "K-1016"]
PRODUKTE_GESPERRT = ["P-114", "P-115", "P-116", "P-117", "P-118", "P-119", "P-107", "P-120"]
TEXT_ORDNER = ["akten", "angebotseingang", "notizbuch"]
# Regel 6: Begriffe aus Tag 2
VO_BEGRIFFE = [r"Grenzwert", r"mg/l", r"µg/l", r"Verordnung \(EU\)", r"Berichtigung"]
# Regel 9 (Nachtrag 21.11.2026): «Sthamer» ist erlaubt
NAMEN_GESPERRT = r"hsg|gallen|unisg|itmp|pfefferminz|minzia|holzweid"
# Regel 15: gesperrte Begriffe und Felder aus früheren Fassungen der Übungswelt (kodiert, damit sie hier
# nicht im Klartext stehen)
THEMA_GESPERRT = base64.b64decode("Zmx1b3J8cGZhc3xmcmVlZm9hbXx1bXN0ZWxsdW5nfGRhdGVuYXVmbmFobWV8YWZmZi1mcmVpfHJlZ3VsYXRvcnk=").decode("utf-8")
FELDER_GESPERRT = base64.b64decode("YmFzaXMscHJvZHVrdGxpbmllLGZsdW9yZnJlaV9kZWtsYXJpZXJ0LG5hY2hmb2xnZXJfaWQsZGF0ZW5hdWZuYWhtZV9hbSx6dW1pc2NocmF0ZV9hbmxhZ2UsenVtaXNjaHJhdGVfY3JtLHp1bWlzY2hyYXRlX3Byb3plbnQscGZhc193ZXJ0LHBmYXNfZWluaGVpdCxiZW1lcmt1bmcsc2V2ZXNv").decode("utf-8").split(",")
TEXT_ENDUNGEN = {".md", ".eml", ".csv", ".json", ".txt", ".html"}
AUSGENOMMEN = {"werkzeuge", "meine-ergebnisse", ".claude"}


def lies_csv(name: str, ordner: Path = DATEN) -> list:
    with open(ordner / name, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def quelle() -> tuple[dict, dict, list]:
    k = {x["id"]: x for x in json.loads((QUELLE / "kunden.json").read_text(encoding="utf-8"))}
    p = {x["id"]: x for x in json.loads((QUELLE / "produkte.json").read_text(encoding="utf-8"))}
    l = json.loads((QUELLE / "lieferungen.json").read_text(encoding="utf-8"))
    return k, p, l


def liter(z: dict) -> int:
    if z["menge_l"] != "":
        return int(z["menge_l"])
    return int(z["menge"]) * GEBINDE_L[z["einheit"]]


def eindeutig(auftraege: list) -> list:
    """Doppelimporte entfernen (gleiche auftrag_id + position nur einmal)."""
    gesehen = set()
    aus = []
    for z in auftraege:
        s = (z["auftrag_id"], z["position"])
        if s in gesehen:
            continue
        gesehen.add(s)
        aus.append(z)
    return aus


def textdateien() -> list:
    aus = []
    for pfad in sorted(TAG1.rglob("*")):
        if not pfad.is_file() or pfad.suffix.lower() not in TEXT_ENDUNGEN:
            continue
        rel = pfad.relative_to(TAG1)
        if rel.parts[0] in AUSGENOMMEN:
            continue
        aus.append(pfad)
    return aus


def _r2(x: float) -> float:
    return round(x + 0.0, 2)


def _konzernkurse(daten: Path) -> dict:
    return json.loads((daten / "kennzahlen.json").read_text(encoding="utf-8"))["konzernkurse"]["kurse"]


# --------------------------------------------------------------------------
# Regeln
# --------------------------------------------------------------------------


def pruefe_alles(daten: Path = DATEN) -> list:
    fehler = []
    kq, pq, lq = quelle()
    kunden = lies_csv("kunden.csv", daten)
    produkte = lies_csv("produkte.csv", daten)
    ls = lies_csv("lieferstellen.csv", daten)
    auftraege = lies_csv("auftraege.csv", daten)
    rekl = lies_csv("reklamationen.csv", daten) if (daten / "reklamationen.csv").exists() else []
    preise = lies_csv("preisliste_2025.csv", daten) + lies_csv("preisliste_2026.csv", daten)
    prod = {p["id"]: p for p in produkte}
    ls_von = {x["lieferstelle_id"]: x for x in ls}

    # Umfang
    if len(kunden) != 32 or len(produkte) != 27 or len(ls) != 136:
        fehler.append("Umfang: %d Kunden, %d Produkte, %d Lieferstellen (erwartet 32/27/136)"
                      % (len(kunden), len(produkte), len(ls)))
    if not 3000 <= len(auftraege) <= 4500:
        fehler.append("Umfang auftraege.csv: %d Positionen (erwartet 3.000-4.500)" % len(auftraege))

    # Regel 1: IDs existieren in Johannes' Daten (K-9xxx erlaubt)
    def k_ok(kid):
        return kid in kq or re.fullmatch(r"K-9\d{3}", kid) is not None
    for name, zeilen, kf, pf in [("kunden", kunden, "id", None), ("produkte", produkte, None, "id"),
                                 ("lieferstellen", ls, "kunde_id", "aktuelles_produkt_id"),
                                 ("auftraege", auftraege, "kunde_id", "produkt_id"),
                                 ("reklamationen", rekl, "kunde_id", "produkt_id"),
                                 ("preislisten", preise, None, "produkt_id")]:
        for z in zeilen:
            if kf and not k_ok(z[kf]):
                fehler.append("Regel 1: %s nennt unbekannten Kunden %s" % (name, z[kf]))
            if pf and z[pf] not in pq:
                fehler.append("Regel 1: %s nennt unbekanntes Produkt %s" % (name, z[pf]))
    for z in auftraege:
        if z["lieferstelle_id"] not in ls_von:
            fehler.append("Regel 1: Lieferstelle %s unbekannt" % z["lieferstelle_id"])
        elif ls_von[z["lieferstelle_id"]]["kunde_id"] != z["kunde_id"]:
            fehler.append("Regel 1: Lieferstelle %s gehört nicht zu %s" % (z["lieferstelle_id"], z["kunde_id"]))

    # Regel 2: letzte Lieferung je Lieferstelle x Produkt x Anwendung (wie in Johannes' lieferungen.json)
    _, zeile_ls = _ls_index(lq)
    letzte = {}
    for z in auftraege:
        if z["art"] in ("Lieferung", "Muster"):
            s = (z["lieferstelle_id"], z["produkt_id"], z["anwendung"])
            letzte[s] = max(letzte.get(s, ""), z["lieferdatum"])
    for l in lq:
        s = (zeile_ls[l["id"]], l["produkt_id"], l["anwendung"])
        if letzte.get(s) != l["letzte_lieferung"]:
            fehler.append("Regel 2: %s letzte Lieferung %s statt %s" % (l["id"], letzte.get(s), l["letzte_lieferung"]))
    for x in ls:
        if x["letzte_lieferung"] != max(l["letzte_lieferung"] for l in lq if zeile_ls[l["id"]] == x["lieferstelle_id"]):
            fehler.append("Regel 2: Lieferstelle %s letzte_lieferung passt nicht" % x["lieferstelle_id"])

    # Regel 3: K-1029 ruhend
    for z in auftraege:
        if z["kunde_id"] == "K-1029" and z["auftragsdatum"] > "2025-09-30":
            fehler.append("Regel 3: K-1029 hat Auftrag am %s" % z["auftragsdatum"])

    # Regel 4: keine Lieferung vor der Markteinführung
    for z in auftraege:
        if z["lieferdatum"] < prod[z["produkt_id"]]["eingefuehrt_am"]:
            fehler.append("Regel 4: %s vor Einführung geliefert (%s)" % (z["produkt_id"], z["lieferdatum"]))

    # Regel 5: Datumsgrenzen
    for name, zeilen, felder in [("auftraege", auftraege, ["auftragsdatum", "lieferdatum"]),
                                 ("lieferstellen", ls, ["letzte_lieferung", "erstbefuellung_am"]),
                                 ("reklamationen", rekl, ["eingang"]),
                                 ("produkte", produkte, ["eingefuehrt_am", "ausgelaufen_am"])]:
        for z in zeilen:
            for f in felder:
                if z[f] and z[f] > STICHTAG:
                    fehler.append("Regel 5: %s.%s = %s nach Stichtag" % (name, f, z[f]))
    for z in auftraege:
        if z["lieferdatum"] < "2021-01-01" or z["auftragsdatum"] < "2021-01-01":
            fehler.append("Regel 5: Auftrag %s vor 2021" % z["auftrag_id"])
    for pfad in (TAG1 / "notizbuch").rglob("*.md") if (TAG1 / "notizbuch").exists() else []:
        for d in re.findall(r"\b(20\d\d-\d\d-\d\d)\b", pfad.read_text(encoding="utf-8")):
            if d > NOTIZBUCH_ENDE:
                fehler.append("Regel 5: Notizbuch %s nennt %s" % (pfad.name, d))

    # Regel 6: keine Messwert-Felder, keine Begriffe aus Tag 2
    for name in ["kunden.csv", "produkte.csv", "lieferstellen.csv", "auftraege.csv"]:
        with open(daten / name, encoding="utf-8-sig") as f:
            kopf = f.readline().strip().split(",")
        for feld in FELDER_GESPERRT:
            if feld in kopf:
                fehler.append("Regel 6: Feld %s in %s" % (feld, name))
        for feld in kopf:
            if feld.startswith("sdb_") or feld.startswith("tdb_"):
                fehler.append("Regel 6: Feld %s in %s" % (feld, name))
    # eingebettete Bilder und Schriften (base64) nicht durchsuchen: dort entstehen zufällige Treffer wie «Hsg»
    texte = {p: re.sub(r"base64,[A-Za-z0-9+/=]+", "", p.read_text(encoding="utf-8", errors="replace"))
             for p in textdateien()}
    for p, t in texte.items():
        for b in VO_BEGRIFFE:
            if re.search(b, t, re.IGNORECASE):
                fehler.append("Regel 6: «%s» in %s" % (b.replace("\\", ""), p.relative_to(TAG1)))

    # Regel 7: Fallträger aus 2.4 nicht in Akten, Anfragen, Notizbuch
    for p, t in texte.items():
        rel = p.relative_to(TAG1)
        if rel.parts[0] not in TEXT_ORDNER:
            continue
        for kid in FALLTRAEGER_GESPERRT:
            if re.search(r"\b%s\b" % kid, t) or kq[kid]["name"] in t:
                fehler.append("Regel 7: %s in %s" % (kid, rel))
        for pid in PRODUKTE_GESPERRT:
            if re.search(r"\b%s\b" % pid, t) or pq[pid]["name"] in t or prod[pid]["name"] in t:
                fehler.append("Regel 7: %s in %s" % (pid, rel))
        if rel.parts[0] == "akten" and re.search(r"Pumpenstation|Testanlage", t):
            fehler.append("Regel 7: Pumpenstation in %s" % rel)

    # Regel 8: E-Mail-Adressen
    for p, t in texte.items():
        for adr in re.findall(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", t):
            if not (adr.lower().endswith("example.com") or adr.lower().endswith(".invalid")):
                fehler.append("Regel 8: Adresse %s in %s" % (adr, p.relative_to(TAG1)))

    # Regel 9: Namens-Scan
    for p, t in texte.items():
        m = re.search(NAMEN_GESPERRT, t, re.IGNORECASE)
        if m:
            fehler.append("Regel 9: «%s» in %s" % (m.group(0), p.relative_to(TAG1)))

    # Regel 15: keine gesperrten Begriffe in den Tag-1-Daten (Ordner daten/)
    for p in sorted(daten.iterdir()):
        if p.is_file() and p.suffix.lower() in TEXT_ENDUNGEN:
            m = re.search(THEMA_GESPERRT, p.read_text(encoding="utf-8", errors="replace"), re.IGNORECASE)
            if m:
                fehler.append("Regel 15: «%s» in daten/%s" % (m.group(0), p.name))

    # Rechenregeln der Tabellen
    for z in auftraege:
        n = int(z["menge"])
        if z["menge_l"] != "" and int(z["menge_l"]) != n * GEBINDE_L[z["einheit"]]:
            fehler.append("Liter: %s/%s menge_l passt nicht" % (z["auftrag_id"], z["position"]))
        if z["menge_l"] == "" and not (z["quellsystem"] == "ERP-alt" and z["einheit"] == "IBC"):
            fehler.append("Liter: %s/%s menge_l leer" % (z["auftrag_id"], z["position"]))
        if abs(round(n * float(z["preis_netto_je_einheit"]), 2) - float(z["nettobetrag"])) > 0.005:
            fehler.append("Betrag: %s/%s" % (z["auftrag_id"], z["position"]))
        if (n < 0) != (z["art"] in ("Gutschrift", "Retoure")):
            fehler.append("Vorzeichen: %s/%s" % (z["auftrag_id"], z["position"]))
        if z["art"] == "Muster" and float(z["nettobetrag"]) != 0:
            fehler.append("Muster mit Betrag: %s" % z["auftrag_id"])
        alt = z["auftragsdatum"] < "2024-07-01"
        if (z["quellsystem"] == "ERP-alt") != alt:
            fehler.append("Quellsystem: %s" % z["auftrag_id"])
        if z["auftragsart"] not in AUFTRAGSARTEN or z["vertriebsweg"] not in WEGE:
            fehler.append("Auftragsart/Vertriebsweg unzulässig: %s/%s" % (z["auftrag_id"], z["position"]))
        if (z["auftragsart"] == "Notfall") != (z["vertriebsweg"] == "Notfallservice"):
            fehler.append("Notfall ohne Notfallservice: %s/%s" % (z["auftrag_id"], z["position"]))
        if (z["auftragsart"] == "Muster") != (z["art"] == "Muster"):
            fehler.append("Muster: Auftragsart und Art passen nicht: %s/%s" % (z["auftrag_id"], z["position"]))

    # Erstbefüllungen: höchstens eine je Lieferstelle, keine Lieferung davor, Datum in lieferstellen.csv
    erst = {}
    frueheste = {}
    for z in eindeutig(auftraege):
        if z["art"] not in ("Lieferung", "Muster"):
            continue
        frueheste[z["lieferstelle_id"]] = min(frueheste.get(z["lieferstelle_id"], "9999"), z["lieferdatum"])
        if z["auftragsart"] == "Erstbefüllung":
            if z["lieferstelle_id"] in erst:
                fehler.append("Erstbefüllung doppelt an %s" % z["lieferstelle_id"])
            erst[z["lieferstelle_id"]] = z["lieferdatum"]
    for x in ls:
        if x["erstbefuellung_am"] != erst.get(x["lieferstelle_id"], ""):
            fehler.append("Lieferstelle %s: erstbefuellung_am passt nicht zu den Aufträgen" % x["lieferstelle_id"])
        if x["erstbefuellung_am"] and frueheste.get(x["lieferstelle_id"]) != x["erstbefuellung_am"]:
            fehler.append("Lieferstelle %s: Lieferung vor der Erstbefüllung" % x["lieferstelle_id"])

    # Reklamationen: Produkt vorher an den Kunden geliefert
    geliefert = {}
    for z in auftraege:
        if z["art"] in ("Lieferung", "Muster"):
            s = (z["kunde_id"], z["produkt_id"])
            geliefert[s] = min(geliefert.get(s, "9999"), z["lieferdatum"])
    for r in rekl:
        if geliefert.get((r["kunde_id"], r["produkt_id"]), "9999") >= r["eingang"]:
            fehler.append("Reklamation %s: Produkt vorher nicht geliefert" % r["rekl_id"])

    # Regeln 11-13: Finanzdaten, Regel 14: Geschäftsbefunde
    fehler += pruefe_finanzen(daten)
    fehler += pruefe_geschaeft(daten)
    return fehler


def _ls_index(lq: list) -> tuple[dict, dict]:
    """Wie erzeuge_daten.lieferstellen_index: (kunde, anlage) -> LS-ID; Lieferzeile -> LS-ID."""
    ls_von = {}
    zeile_ls = {}
    for l in lq:
        s = (l["kunde_id"], l["anlage"])
        if s not in ls_von:
            ls_von[s] = "LS-%04d" % (len(ls_von) + 1)
        zeile_ls[l["id"]] = ls_von[s]
    return ls_von, zeile_ls


# --------------------------------------------------------------------------
# Geschäftsentwicklung (Drill 1): Absatz, Umsatz, Auftragsart, Vertriebsweg, Kunden
# --------------------------------------------------------------------------


def geschaeft(daten: Path = DATEN) -> dict:
    """Kennzahlen der Geschäftsentwicklung nach den Definitionen in kennzahlen.json (Konzernkurs)."""
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    produkte = {p["id"]: p for p in lies_csv("produkte.csv", daten)}
    pos = eindeutig(lies_csv("auftraege.csv", daten))
    kk = _konzernkurse(daten)

    def eur(z: dict) -> float:
        b = float(z["nettobetrag"])
        return b if z["waehrung"] == "EUR" else b * kk[z["lieferdatum"][:4]][z["waehrung"]]

    def tabelle(gruppe, zeilen=None) -> dict:
        s = {}
        for z in pos if zeilen is None else zeilen:
            a = s.setdefault(gruppe(z), {j: [0, 0.0, 0] for j in JAHRE})[z["lieferdatum"][:4]]
            if z["art"] != "Muster":
                a[0] += liter(z)
            a[1] += eur(z)
            a[2] += 1
        return {g: {j: {"absatz_l": v[0], "umsatz_eur": _r2(v[1]), "positionen": v[2]} for j, v in jahre.items()}
                for g, jahre in sorted(s.items())}

    def wachstum(gruppe) -> dict:
        t = tabelle(gruppe)
        aus = {}
        for g, j in t.items():
            u25, u26 = j["2025"]["umsatz_eur"], j["2026"]["umsatz_eur"]
            l25, l26 = j["2025"]["absatz_l"], j["2026"]["absatz_l"]
            n = min(j["2025"]["positionen"], j["2026"]["positionen"])
            w = (u26 / u25 - 1) if u25 else None
            if n < 20 or w is None:
                ampel = "Lücke"
            else:
                ampel = "Wachstum" if w > 0.05 + 1e-12 else ("Rückgang" if w < -0.05 - 1e-12 else "stabil")
            aus[g] = {"umsatz_2025_eur": u25, "umsatz_2026_eur": u26, "veraenderung_umsatz": round(w, 4) if w is not None else None,
                      "absatz_2025_l": l25, "absatz_2026_l": l26,
                      "veraenderung_absatz": round(l26 / l25 - 1, 4) if l25 else None,
                      "positionen_2025": j["2025"]["positionen"], "positionen_2026": j["2026"]["positionen"],
                      "ampel": ampel}
        return aus

    gesamt = tabelle(lambda z: "gesamt")["gesamt"]
    art = tabelle(lambda z: z["auftragsart"])
    nachfuell = {}
    for j in JAHRE:
        alle = gesamt[j]["absatz_l"]
        nachfuell[j] = {"nachfuell_anteil": round(art.get("Nachfüllung", {}).get(j, {"absatz_l": 0})["absatz_l"] / alle, 4),
                        "projektanteil": round(art.get("Erstbefüllung", {}).get(j, {"absatz_l": 0})["absatz_l"] / alle, 4),
                        "notfall_anteil": round(art.get("Notfall", {}).get(j, {"absatz_l": 0})["absatz_l"] / alle, 4)}

    def top5(jahr: str, ohne_notfall: bool = False) -> dict:
        u = {}
        for z in pos:
            if z["lieferdatum"][:4] == jahr and not (ohne_notfall and z["vertriebsweg"] == "Notfallservice"):
                u[z["kunde_id"]] = u.get(z["kunde_id"], 0.0) + eur(z)
        rang = sorted(u.items(), key=lambda x: (-x[1], x[0]))
        summe = sum(u.values())
        oben = sum(v for _, v in rang[:5])
        return {"top5": [{"kunde_id": k, "name": kunden[k]["name"], "umsatz_eur": _r2(v)} for k, v in rang[:5]],
                "top5_umsatz_eur": _r2(oben), "gesamt_umsatz_eur": _r2(summe), "top5_anteil": round(oben / summe, 4),
                "kunden_mit_umsatz": len(u)}

    letzte = {}
    for z in pos:
        if z["art"] == "Lieferung":
            letzte[z["kunde_id"]] = max(letzte.get(z["kunde_id"], ""), z["lieferdatum"])
    status = {}
    for k in sorted(kunden):
        d = letzte.get(k, "")
        s = "aktiv" if d >= "2026-03-01" else ("ruhend" if d >= "2025-03-01" else "verloren")
        status[k] = {"letzte_lieferung": d, "kundenstatus": s, "status_kundenstamm": kunden[k]["status"]}
    zaehl = {s: sorted(k for k, v in status.items() if v["kundenstatus"] == s) for s in ("aktiv", "ruhend", "verloren")}
    umsatz25 = tabelle(lambda z: z["kunde_id"])
    ruhend_umsatz_2025 = _r2(sum(umsatz25[k]["2025"]["umsatz_eur"] for k in zaehl["ruhend"] + zaehl["verloren"] if k in umsatz25))

    erstbef = []
    for z in pos:
        if z["auftragsart"] == "Erstbefüllung" and z["art"] == "Lieferung":
            erstbef.append({"lieferdatum": z["lieferdatum"], "kunde_id": z["kunde_id"], "segment": kunden[z["kunde_id"]]["segment"],
                            "lieferstelle_id": z["lieferstelle_id"], "anwendung": z["anwendung"], "liter": liter(z),
                            "umsatz_eur": _r2(eur(z)), "vertriebsweg": z["vertriebsweg"]})
    erstbef.sort(key=lambda e: (e["lieferdatum"], e["lieferstelle_id"]))
    gross = {}
    for e in erstbef:
        if e["anwendung"] == "stationaere_anlage" and e["liter"] >= 2500:
            j = e["lieferdatum"][:4]
            gross[j] = gross.get(j, 0) + 1

    notfall = [{"lieferdatum": z["lieferdatum"], "kunde_id": z["kunde_id"], "liter": liter(z), "umsatz_eur": _r2(eur(z)),
                "produkt_id": z["produkt_id"]} for z in pos if z["auftragsart"] == "Notfall"]
    groesste = max((z for z in pos if z["art"] == "Lieferung"), key=lambda z: liter(z))

    weg = tabelle(lambda z: z["vertriebsweg"])
    art_weg = tabelle(lambda z: z["vertriebsweg"] + "|" + z["auftragsart"])
    delta = {}
    for g, t in [("auftragsart", art), ("vertriebsweg", weg)]:
        delta[g] = {k: {"absatz_l": v["2026"]["absatz_l"] - v["2025"]["absatz_l"],
                        "umsatz_eur": _r2(v["2026"]["umsatz_eur"] - v["2025"]["umsatz_eur"])} for k, v in t.items()}
    delta["gesamt"] = {"absatz_l": gesamt["2026"]["absatz_l"] - gesamt["2025"]["absatz_l"],
                       "umsatz_eur": _r2(gesamt["2026"]["umsatz_eur"] - gesamt["2025"]["umsatz_eur"])}
    return {
        "gesamt_je_jahr": gesamt,
        "auftragsart_je_jahr": art,
        "vertriebsweg_je_jahr": weg,
        "vertriebsweg_auftragsart_je_jahr": art_weg,
        "segment_je_jahr": tabelle(lambda z: kunden[z["kunde_id"]]["segment"]),
        "land_je_jahr": tabelle(lambda z: kunden[z["kunde_id"]]["land"]),
        "anwendung_je_jahr": tabelle(lambda z: z["anwendung"]),
        "schaumart_je_jahr": tabelle(lambda z: produkte[z["produkt_id"]]["schaumart"]),
        "nachfuell_anteil": nachfuell,
        "veraenderung_2026_gegen_2025": delta,
        "wachstum_ampel_2026": {
            "segment": wachstum(lambda z: kunden[z["kunde_id"]]["segment"]),
            "vertriebsweg": wachstum(lambda z: z["vertriebsweg"]),
            "land": wachstum(lambda z: kunden[z["kunde_id"]]["land"]),
            "auftragsart": wachstum(lambda z: z["auftragsart"]),
        },
        "top5": {"2025": top5("2025"), "2026": top5("2026"), "2026_ohne_notfall": top5("2026", True)},
        "kundenstatus": {"je_kunde": status, "anzahl": {s: len(v) for s, v in zaehl.items()}, "kunden": zaehl,
                         "umsatz_2025_der_ruhenden_und_verlorenen_eur": ruhend_umsatz_2025},
        "erstbefuellungen": erstbef,
        "erstbefuellungen_stationaer_ab_2500_l_je_jahr": gross,
        "notfall_positionen": notfall,
        "groesste_lieferposition": {"auftrag_id": groesste["auftrag_id"], "lieferdatum": groesste["lieferdatum"],
                                    "kunde_id": groesste["kunde_id"], "liter": liter(groesste),
                                    "auftragsart": groesste["auftragsart"]},
    }


def pruefe_geschaeft(daten: Path = DATEN) -> list:
    """Regel 14: Die Geschäftsbefunde für Drill 1 und 2 sind eindeutig."""
    fehler = []
    g = geschaeft(daten)
    art, weg, ges = g["auftragsart_je_jahr"], g["vertriebsweg_je_jahr"], g["gesamt_je_jahr"]
    nf25, nf26 = art["Nachfüllung"]["2025"]["absatz_l"], art["Nachfüllung"]["2026"]["absatz_l"]
    eb25, eb26 = art["Erstbefüllung"]["2025"]["absatz_l"], art["Erstbefüllung"]["2026"]["absatz_l"]
    if not abs(nf26 / nf25 - 1) <= 0.05:  # «stabil» wie in der Wachstumsampel
        fehler.append("Regel 14: Nachfüllgeschäft 2026 nicht stabil (%d gegen %d l)" % (nf26, nf25))
    if not eb25 >= 5 * max(eb26, 1):
        fehler.append("Regel 14: Erstbefüllungen 2025 nicht klar über 2026")
    ohne_nf = lambda j: ges[j]["absatz_l"] - art.get("Notfall", {}).get(j, {"absatz_l": 0})["absatz_l"]
    luecke = ohne_nf("2025") - ohne_nf("2026")
    if not (luecke > 0 and (eb25 - eb26) >= 0.8 * luecke):
        fehler.append("Regel 14: Mengenrückgang 2026 nicht überwiegend durch weniger Erstbefüllungen erklärt")
    h = [weg["Händler"][j]["absatz_l"] for j in JAHRE[:6]]
    if not all(b > a for a, b in zip(h, h[1:])) or not h[5] >= 1.05 * h[4]:
        fehler.append("Regel 14: Händlergeschäft wächst nicht jedes Jahr (%s)" % h)
    d = [weg["direkt"][j]["absatz_l"] for j in JAHRE[:6]]
    if all(b > a for a, b in zip(d, d[1:])) or not d[5] < 0.9 * d[4]:
        fehler.append("Regel 14: Direktgeschäft schwankt nicht bzw. fällt 2026 nicht klar (%s)" % d)
    r = [weg["Rahmenvertrag"][j]["absatz_l"] for j in ("2025", "2026")]
    if not abs(r[1] / r[0] - 1) <= 0.05:
        fehler.append("Regel 14: Rahmenverträge 2026 nicht stabil (%s)" % r)
    t = g["top5"]["2026"]["top5_anteil"]
    if not 0.4 <= t <= 0.7 or not g["top5"]["2026_ohne_notfall"]["top5_anteil"] < t:
        fehler.append("Regel 14: Top-5-Anteil 2026 unplausibel (%.3f)" % t)
    ks = g["kundenstatus"]["kunden"]
    if "K-1029" not in ks["ruhend"] + ks["verloren"]:
        fehler.append("Regel 14: K-1029 nicht ruhend")
    gp = g["groesste_lieferposition"]
    if not (gp["lieferdatum"] == "2026-09-22" and gp["liter"] == 24000 and gp["auftragsart"] == "Notfall"):
        fehler.append("Regel 14: Notfall 22.09.2026 (24.000 l) ist nicht die grösste Position")
    return fehler


# --------------------------------------------------------------------------
# Finanzdaten (Drill 2): Kennzahlen nach kennzahlen.json, Regeln 11-13
# --------------------------------------------------------------------------

FINANZ_DATEIEN = ["herstellkosten.csv", "fracht.csv", "kurse.csv", "budget_2026.csv"]


def finanzen(daten: Path = DATEN) -> dict:
    """Deckungsbeitrag, Plan-Ist-Brücke, Fremdwährung und Rabatte nach den Definitionen in kennzahlen.json."""
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    schaumart = {p["id"]: p["schaumart"] for p in lies_csv("produkte.csv", daten)}
    pos = eindeutig(lies_csv("auftraege.csv", daten))
    hk = {(h["produkt_id"], h["jahr"]): float(h["rohstoff_eur_l"]) + float(h["fertigung_eur_l"])
          for h in lies_csv("herstellkosten.csv", daten)}
    fracht = {f["auftrag_id"]: float(f["frachtkosten_eur"]) for f in lies_csv("fracht.csv", daten)}
    kurse = {(k["monat"], k["waehrung"]): k for k in lies_csv("kurse.csv", daten)}
    budget = lies_csv("budget_2026.csv", daten)
    kk = _konzernkurse(daten)
    listen = {}
    for j in ("2025", "2026"):
        for x in lies_csv("preisliste_%s.csv" % j, daten):
            listen[(j, x["produkt_id"], x["gebinde"])] = float(x["preis_netto_eur"])

    liter_auftrag = {}
    for z in pos:
        if z["art"] in ("Lieferung", "Muster"):
            liter_auftrag[z["auftrag_id"]] = liter_auftrag.get(z["auftrag_id"], 0) + liter(z)

    def werte(z: dict) -> dict:
        """Kennzahlen einer Position: Liter netto, Umsatz (Konzern-, Plan-, Ist-Monatskurs), Kosten."""
        j = z["lieferdatum"][:4]
        lt = liter(z)
        betrag = float(z["nettobetrag"])
        w = z["waehrung"]
        if w == "EUR":
            konzern = plan = ist = betrag
        else:
            konzern = betrag * kk[j][w]
            k = kurse.get((z["lieferdatum"][:7], w))
            plan = betrag * float(k["plankurs_eur"]) if k else None
            ist = betrag * float(k["ist_kurs_eur"]) if k else None
        herst = 0.0 if z["art"] == "Gutschrift" else lt * hk[(z["produkt_id"], j)]
        fr = 0.0
        if z["art"] in ("Lieferung", "Muster"):
            fr = fracht[z["auftrag_id"]] * lt / liter_auftrag[z["auftrag_id"]]
        return {"liter": 0 if z["art"] == "Muster" else lt, "konzern": konzern, "plan": plan, "ist": ist,
                "hk": herst, "fracht": fr}

    def db_tabelle(jahr: str, schluessel, ohne_notfall: bool) -> dict:
        s = {}
        for z in pos:
            if z["lieferdatum"][:4] != jahr or (ohne_notfall and z["vertriebsweg"] == "Notfallservice"):
                continue
            w = werte(z)
            a = s.setdefault(schluessel(z), [0, 0.0, 0.0, 0.0])
            a[0] += w["liter"]
            a[1] += w["konzern"]
            a[2] += w["hk"]
            a[3] += w["fracht"]
        aus = {}
        for k in sorted(s):
            lt, um, herst, fr = s[k]
            db = um - herst - fr
            aus[k] = {"liter": lt, "umsatz_eur": _r2(um), "herstellkosten_eur": _r2(herst), "fracht_eur": _r2(fr),
                      "db_eur": _r2(db), "db_marge": round(db / um, 4) if um else None,
                      "db_vor_fracht_marge": round((um - herst) / um, 4) if um else None,
                      "db_je_liter_eur": round(db / lt, 4) if lt else None}
        return aus

    db = {}
    for j in ("2025", "2026"):
        db[j] = {
            "segment": db_tabelle(j, lambda z: kunden[z["kunde_id"]]["segment"], False),
            "vertriebsweg": db_tabelle(j, lambda z: z["vertriebsweg"], False),
            "schaumart": db_tabelle(j, lambda z: schaumart[z["produkt_id"]], False),
            "schaumart_ohne_notfall": db_tabelle(j, lambda z: schaumart[z["produkt_id"]], True),
            "auftragsart": db_tabelle(j, lambda z: z["auftragsart"], False),
            "segment_vertriebsweg": db_tabelle(j, lambda z: kunden[z["kunde_id"]]["segment"] + "|" + z["vertriebsweg"], False),
            "kunde": db_tabelle(j, lambda z: z["kunde_id"], False),
            "gesamt": db_tabelle(j, lambda z: "gesamt", False)["gesamt"],
            "gesamt_ohne_notfall": db_tabelle(j, lambda z: "gesamt", True)["gesamt"],
        }

    # Plan-Ist-Brücke 2026, Zellen Segment x Vertriebsweg
    plan = {}
    for b in budget:
        c = (b["segment"], b["vertriebsweg"])
        p = plan.setdefault(c, [0, 0.0, 0.0])
        p[0] += int(b["menge_l"])
        p[1] += float(b["umsatz_eur"])
        p[2] += float(b["db_eur"])
    ist = {}
    notfall = {"umsatz_ist": 0.0, "umsatz_plankurs": 0.0, "kosten": 0.0, "liter": 0}
    for z in pos:
        if z["lieferdatum"][:4] != "2026":
            continue
        w = werte(z)
        if z["vertriebsweg"] == "Notfallservice":
            notfall["umsatz_ist"] += w["ist"]
            notfall["umsatz_plankurs"] += w["plan"]
            notfall["kosten"] += w["hk"] + w["fracht"]
            notfall["liter"] += w["liter"]
            continue
        c = (kunden[z["kunde_id"]]["segment"], z["vertriebsweg"])
        a = ist.setdefault(c, [0, 0.0, 0.0, 0.0])
        a[0] += w["liter"]
        a[1] += w["plan"]
        a[2] += w["ist"]
        a[3] += w["hk"] + w["fracht"]
    ohne_plan = sorted("%s|%s" % c for c in ist if c not in plan)
    mp = sum(p[0] for p in plan.values())
    up = sum(p[1] for p in plan.values())
    dp = sum(p[2] for p in plan.values())
    mi = sum(a[0] for a in ist.values())
    ui_plan = sum(a[1] for a in ist.values())
    ui_ist = sum(a[2] for a in ist.values())
    ki = sum(a[3] for a in ist.values())
    preis_c = {c: p[1] / p[0] for c, p in plan.items()}
    dbl_c = {c: p[2] / p[0] for c, p in plan.items()}
    preiseffekt = sum(a[1] - a[0] * preis_c.get(c, 0.0) for c, a in ist.items())
    fx = ui_ist - ui_plan
    nf_db = notfall["umsatz_ist"] - notfall["kosten"]
    umsatz_bruecke = {
        "plan": _r2(up),
        "mengeneffekt": _r2((mi - mp) * up / mp),
        "mixeffekt": _r2(sum(a[0] * preis_c.get(c, 0.0) for c, a in ist.items()) - mi * up / mp),
        "preiseffekt": _r2(preiseffekt),
        "fremdwaehrungseffekt": _r2(fx),
        "notfallservice": _r2(notfall["umsatz_ist"]),
        "ist": _r2(ui_ist + notfall["umsatz_ist"]),
    }
    db_bruecke = {
        "plan": _r2(dp),
        "mengeneffekt": _r2((mi - mp) * dp / mp),
        "mixeffekt": _r2(sum(a[0] * dbl_c.get(c, 0.0) for c, a in ist.items()) - mi * dp / mp),
        "preiseffekt": _r2(preiseffekt),
        "kosteneffekt": _r2(sum(a[0] * (preis_c.get(c, 0.0) - dbl_c.get(c, 0.0)) - a[3] for c, a in ist.items())),
        "fremdwaehrungseffekt": _r2(fx),
        "notfallservice": _r2(nf_db),
        "ist": _r2(ui_ist - ki + nf_db),
    }
    zellen = {}
    for c in sorted(set(plan) | set(ist)):
        p = plan.get(c, [0, 0.0, 0.0])
        a = ist.get(c, [0, 0.0, 0.0, 0.0])
        zellen["%s|%s" % c] = {"plan_liter": p[0], "ist_liter": a[0], "plan_umsatz_eur": _r2(p[1]),
                               "ist_umsatz_plankurs_eur": _r2(a[1]), "plan_db_eur": _r2(p[2]),
                               "ist_db_eur": _r2(a[2] - a[3])}
    weg_plan_ist = {}
    for c, v in zellen.items():
        w = c.split("|")[1]
        a = weg_plan_ist.setdefault(w, {"plan_liter": 0, "ist_liter": 0})
        a["plan_liter"] += v["plan_liter"]
        a["ist_liter"] += v["ist_liter"]
    bruecke = {
        "methode": "Zellen Segment x Vertriebsweg; siehe kennzahlen.json plan_ist_bruecke",
        "plan_liter": mp, "ist_liter_ohne_notfall": mi, "notfall_liter": notfall["liter"],
        "db_marge_plan": round(dp / up, 4),
        "db_marge_ist": round(db_bruecke["ist"] / umsatz_bruecke["ist"], 4),
        "db_marge_ist_ohne_notfall": round((ui_ist - ki) / ui_ist, 4),
        "db_ist_ohne_notfall": _r2(ui_ist - ki),
        "umsatz": umsatz_bruecke, "deckungsbeitrag": db_bruecke, "zellen_ohne_plan": ohne_plan,
        "zellen": zellen, "vertriebsweg_plan_ist_liter": weg_plan_ist,
    }
    monate = {}
    for b in budget:
        m = monate.setdefault(b["monat"], {"plan_liter": 0, "plan_umsatz_eur": 0.0, "ist_liter": 0, "ist_umsatz_eur": 0.0})
        m["plan_liter"] += int(b["menge_l"])
        m["plan_umsatz_eur"] += float(b["umsatz_eur"])
    for z in pos:
        if z["lieferdatum"][:4] == "2026":
            w = werte(z)
            m = monate[z["lieferdatum"][:7]]
            m["ist_liter"] += w["liter"]
            m["ist_umsatz_eur"] += w["ist"]
    for m in monate.values():
        m["plan_umsatz_eur"] = _r2(m["plan_umsatz_eur"])
        m["ist_umsatz_eur"] = _r2(m["ist_umsatz_eur"])
    bruecke["monate_inkl_notfall"] = monate

    # Fremdwährung je Währung 2026 und Rabattquote 2025/2026
    fw = {}
    for z in pos:
        if z["lieferdatum"][:4] == "2026" and z["waehrung"] != "EUR":
            w = werte(z)
            a = fw.setdefault(z["waehrung"], {"betrag_fw": 0.0, "eur_plankurs": 0.0, "eur_ist": 0.0})
            a["betrag_fw"] += float(z["nettobetrag"])
            a["eur_plankurs"] += w["plan"]
            a["eur_ist"] += w["ist"]
    for w in ("CHF", "GBP", "NOK"):
        a = fw.setdefault(w, {"betrag_fw": 0.0, "eur_plankurs": 0.0, "eur_ist": 0.0})
        a["effekt_eur"] = _r2(a["eur_ist"] - a["eur_plankurs"])
        for k in ("betrag_fw", "eur_plankurs", "eur_ist"):
            a[k] = _r2(a[k])
    rabatt = {}
    for j in ("2025", "2026"):
        s = {}
        for z in pos:
            if z["lieferdatum"][:4] != j or z["art"] != "Lieferung" or z["vertriebsweg"] == "Notfallservice":
                continue
            lw = int(z["menge"]) * listen[(j, z["produkt_id"], z["einheit"])]
            netto = werte(z)["konzern"]
            quartal = "Q%d" % ((int(z["lieferdatum"][5:7]) - 1) // 3 + 1)
            for k in ("gesamt", "weg:" + z["vertriebsweg"], "lieferquartal:" + quartal):
                a = s.setdefault(k, [0.0, 0.0])
                a[0] += lw
                a[1] += netto
        rabatt[j] = {k: {"listenwert_eur": _r2(v[0]), "netto_eur": _r2(v[1]), "rabattquote": round(1 - v[1] / v[0], 4) + 0.0}
                     for k, v in sorted(s.items())}
    r25 = rabatt["2025"]["gesamt"]["rabattquote"]
    r26 = rabatt["2026"]["gesamt"]["rabattquote"]
    return {
        "deckungsbeitrag": db,
        "plan_ist_2026": bruecke,
        "fremdwaehrung_2026": {"je_waehrung": fw, "summe_eur": _r2(sum(a["effekt_eur"] for a in fw.values()))},
        "rabatte": {"quoten": rabatt, "listenpreiserhoehung_2026": 0.04,
                    "realisierte_preiserhoehung_naeherung": round(1.04 * (1 - r26) / (1 - r25) - 1, 4),
                    "hinweis": "Näherung bei gleichem Produkt- und Gebindemix: 1,04 x (1 - Quote 2026) / (1 - Quote 2025) - 1"},
    }


def pruefe_finanzen(daten: Path = DATEN) -> list:
    """Regeln 11-13: Querbezüge der Finanzdaten und die eingebauten Erkenntnisse."""
    fehler = []
    if not all((daten / n).exists() for n in FINANZ_DATEIEN):
        return ["Regel 11: Finanzdateien fehlen (%s)" % ", ".join(FINANZ_DATEIEN)]
    pos = eindeutig(lies_csv("auftraege.csv", daten))
    hk = lies_csv("herstellkosten.csv", daten)
    fr = lies_csv("fracht.csv", daten)
    kurse = lies_csv("kurse.csv", daten)
    budget = lies_csv("budget_2026.csv", daten)
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    kz = json.loads((daten / "kennzahlen.json").read_text(encoding="utf-8"))
    kk = kz["konzernkurse"]["kurse"]

    # Regel 11: Vollständigkeit und Querbezüge
    hk_schl = {(h["produkt_id"], h["jahr"]) for h in hk}
    if len(hk_schl) != len(hk) or len(hk) != 27 * 7:
        fehler.append("Regel 11: herstellkosten.csv hat %d Zeilen (erwartet 27 x 7, eindeutig)" % len(hk))
    for z in pos:
        if (z["produkt_id"], z["lieferdatum"][:4]) not in hk_schl:
            fehler.append("Regel 11: keine Herstellkosten für %s %s" % (z["produkt_id"], z["lieferdatum"][:4]))
            break
    braucht = {}
    for z in pos:
        if z["art"] in ("Lieferung", "Muster"):
            braucht[z["auftrag_id"]] = braucht.get(z["auftrag_id"], 0) + liter(z)
    fr_von = {}
    for f in fr:
        if f["auftrag_id"] in fr_von:
            fehler.append("Regel 11: Fracht für %s doppelt" % f["auftrag_id"])
        fr_von[f["auftrag_id"]] = f
    if set(fr_von) != set(braucht):
        fehler.append("Regel 11: fracht.csv passt nicht zu den Aufträgen (%d fehlen, %d zu viel)"
                      % (len(set(braucht) - set(fr_von)), len(set(fr_von) - set(braucht))))
    for aid, f in fr_von.items():
        if aid in braucht and int(f["liter"]) != braucht[aid]:
            fehler.append("Regel 11: Fracht %s mit %s l statt %d l" % (aid, f["liter"], braucht[aid]))
        if float(f["frachtkosten_eur"]) <= 0:
            fehler.append("Regel 11: Fracht %s ohne Betrag" % aid)
    if len(kurse) != 36:
        fehler.append("Regel 11: kurse.csv hat %d Zeilen (erwartet 12 Monate x 3 Währungen)" % len(kurse))
    for w in ("CHF", "GBP", "NOK"):
        ist = [float(k["ist_kurs_eur"]) for k in kurse if k["waehrung"] == w]
        if ist and abs(sum(ist) / len(ist) - kk["2026"][w]) > 1e-6:
            fehler.append("Regel 11: Ist-Monatskurse %s mitteln nicht auf den Konzernkurs 2026" % w)
    preis_zelle = {}
    segmente = {k["segment"] for k in kunden.values()}
    for b in budget:
        if abs(round(int(b["menge_l"]) * float(b["preis_eur_l"]), 2) - float(b["umsatz_eur"])) > 0.005:
            fehler.append("Regel 11: Budget %s %s %s: Umsatz passt nicht" % (b["monat"], b["segment"], b["vertriebsweg"]))
        c = (b["segment"], b["vertriebsweg"])
        if preis_zelle.setdefault(c, b["preis_eur_l"]) != b["preis_eur_l"]:
            fehler.append("Regel 11: Budget-Preis je Liter schwankt in %s|%s" % c)
        if b["vertriebsweg"] not in ("direkt", "Händler", "Rahmenvertrag") or b["segment"] not in segmente \
                or b["monat"][:4] != "2026":
            fehler.append("Regel 11: Budgetzeile unzulässig: %s" % b)
    ziel = kz["ziele"]["2026"]
    if abs(ziel["nettoumsatz_eur"] - sum(float(b["umsatz_eur"]) for b in budget)) > 0.01 \
            or ziel["absatz_l"] != sum(int(b["menge_l"]) for b in budget):
        fehler.append("Regel 11: Ziele 2026 in kennzahlen.json passen nicht zum Budget")

    f = finanzen(daten)
    pi = f["plan_ist_2026"]
    if pi["zellen_ohne_plan"]:
        fehler.append("Regel 11: Ist-Zellen ohne Budget: %s" % ", ".join(pi["zellen_ohne_plan"]))

    # Regel 12: Brücken gehen auf
    for name in ("umsatz", "deckungsbeitrag"):
        b = pi[name]
        summe = sum(v for k, v in b.items() if k != "ist")
        if abs(summe - b["ist"]) > 0.05:
            fehler.append("Regel 12: %s-Brücke geht nicht auf (%.2f gegen %.2f)" % (name, summe, b["ist"]))

    # Regel 13: eingebaute Erkenntnisse (eindeutig)
    for j in ("2025", "2026"):
        dw = f["deckungsbeitrag"][j]["vertriebsweg"]
        if not dw["Händler"]["db_marge"] + 0.08 < dw["direkt"]["db_marge"]:
            fehler.append("Regel 13: DB-Marge Händler %s nicht klar unter direkt" % j)
    if not f["deckungsbeitrag"]["2026"]["vertriebsweg"]["Notfallservice"]["db_marge"] > \
            f["deckungsbeitrag"]["2026"]["vertriebsweg"]["direkt"]["db_marge"]:
        fehler.append("Regel 13: Notfallservice 2026 nicht mit der höchsten Marge")
    ub, dbb = pi["umsatz"], pi["deckungsbeitrag"]
    if not (ub["mengeneffekt"] < -100000 and pi["ist_liter_ohne_notfall"] < pi["plan_liter"]):
        fehler.append("Regel 13: keine klare Mengenlücke Plan-Ist 2026")
    if not (dbb["preiseffekt"] > 2000):
        fehler.append("Regel 13: Preiseffekt im Deckungsbeitrag nicht positiv")
    if not abs(dbb["mixeffekt"]) < 0.5 * abs(dbb["mengeneffekt"]):
        fehler.append("Regel 13: Mixeffekt grösser als die halbe Mengenlücke")
    if not (dbb["preiseffekt"] + max(dbb["mixeffekt"], 0) < -dbb["mengeneffekt"]):
        fehler.append("Regel 13: Preis und Mix kompensieren die Mengenlücke mehr als vollständig")
    if not abs(dbb["fremdwaehrungseffekt"]) < 0.005 * ub["ist"]:
        fehler.append("Regel 13: Fremdwährungseffekt nicht klein")
    fw = f["fremdwaehrung_2026"]["je_waehrung"]
    if not (fw["NOK"]["effekt_eur"] < -100 and fw["CHF"]["effekt_eur"] > 100):
        fehler.append("Regel 13: Fremdwährungseffekt NOK/CHF nicht sichtbar")
    rq = f["rabatte"]
    if not (rq["quoten"]["2026"]["gesamt"]["rabattquote"] > rq["quoten"]["2025"]["gesamt"]["rabattquote"] + 0.01
            and 0 < rq["realisierte_preiserhoehung_naeherung"] < 0.03):
        fehler.append("Regel 13: Preiserhöhung 2026 nicht erkennbar nur teilweise durchgesetzt")
    if not dbb["ist"] > dbb["plan"] > dbb["ist"] - dbb["notfallservice"]:
        fehler.append("Regel 13: Notfall-Falle (DB über Plan nur durch Notfallservice) greift nicht")
    return fehler


# --------------------------------------------------------------------------
# Sollwerte (nur für das Lecture-Repo, über erzeuge_daten.py --sollwerte)
# --------------------------------------------------------------------------


def sollwerte(daten: Path = DATEN) -> dict:
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    auftraege = lies_csv("auftraege.csv", daten)
    roh = len(auftraege)
    ohne_dup = eindeutig(auftraege)
    seit = "2025-03-01"
    b = {k["kunde_id"] for k in ohne_dup if k["art"] == "Lieferung" and k["auftragsdatum"] >= seit}
    g = geschaeft(daten)
    f = finanzen(daten)
    return {
        "hinweis": "Sollwerte Tag 1 (roter Faden Geschäftsentwicklung), erzeugt aus tag1/daten. Nicht ins Teilnehmer-Repo.",
        "kunden": {
            "A_kundenstamm": {"DE": sum(1 for k in kunden.values() if k["land"] == "DE"),
                              "ausland": sum(1 for k in kunden.values() if k["land"] != "DE")},
            "B_auftrag_24_monate": {"DE": sum(1 for k in b if kunden[k]["land"] == "DE"),
                                    "ausland": sum(1 for k in b if kunden[k]["land"] != "DE")},
            "C_status_aktiv": {"DE": sum(1 for k in kunden.values() if k["status"] == "aktiv" and k["land"] == "DE"),
                               "ausland": sum(1 for k in kunden.values() if k["status"] == "aktiv" and k["land"] != "DE")},
        },
        "auftraege": {"positionen_roh": roh, "doppelimporte": roh - len(ohne_dup),
                      "muster": sum(1 for z in ohne_dup if z["art"] == "Muster"),
                      "gutschriften_retouren": sum(1 for z in ohne_dup if z["art"] in ("Gutschrift", "Retoure")),
                      "erp_alt_ibc_ohne_liter": sum(1 for z in ohne_dup if z["menge_l"] == ""),
                      "auftragsart": {a: sum(1 for z in ohne_dup if z["auftragsart"] == a) for a in AUFTRAGSARTEN}},
        "kernbefund": kernbefund(g, f),
        "geschaeft": g,
        "finanzen": f,
        **sollwerte_drills(daten),
    }


def kernbefund(g: dict, f: dict) -> dict:
    """Die eindeutige Antwort auf «Wo wachsen wir, wo verlieren wir?» (Zahlen für den Dozententeil)."""
    art, weg = g["auftragsart_je_jahr"], g["vertriebsweg_je_jahr"]
    pi = f["plan_ist_2026"]
    return {
        "absatz_l": {j: g["gesamt_je_jahr"][j]["absatz_l"] for j in ("2024", "2025", "2026")},
        "nachfuellung_l": {j: art["Nachfüllung"][j]["absatz_l"] for j in ("2024", "2025", "2026")},
        "erstbefuellung_l": {j: art["Erstbefüllung"][j]["absatz_l"] for j in ("2024", "2025", "2026")},
        "notfall_l": {j: art.get("Notfall", {}).get(j, {"absatz_l": 0})["absatz_l"] for j in ("2024", "2025", "2026")},
        "haendler_l": {j: weg["Händler"][j]["absatz_l"] for j in JAHRE[:6]},
        "direkt_l": {j: weg["direkt"][j]["absatz_l"] for j in JAHRE[:6]},
        "rahmenvertrag_l": {j: weg["Rahmenvertrag"][j]["absatz_l"] for j in JAHRE[:6]},
        "plan_liter_2026": pi["plan_liter"], "ist_liter_2026_ohne_notfall": pi["ist_liter_ohne_notfall"],
        "antwort": "Wir wachsen im Händlergeschäft (jedes Jahr mehr Liter) und halten das Nachfüllgeschäft stabil; "
                   "wir verlieren 2026 Menge im Projektgeschäft, weil kaum neue grosse Anlagen erstbefüllt wurden "
                   "(2025 viele, 2026 eine kleine) – das erklärt die Mengenlücke zu 2025 und zum Budget. "
                   "Der Notfall vom 22.09.2026 überdeckt das im Umsatz und im Deckungsbeitrag.",
    }


def sollwerte_drills(daten: Path = DATEN) -> dict:
    """Zusätzliche Sollwerte für Drill 0 (Kundenzählweisen) und Drill 1 (Kacheln, Fallen)."""
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    ls = lies_csv("lieferstellen.csv", daten)
    auftraege = lies_csv("auftraege.csv", daten)
    pos = eindeutig(auftraege)
    kk = _konzernkurse(daten)

    def land(ids) -> dict:
        ids = list(ids)
        return {"DE": sum(1 for i in ids if kunden[i]["land"] == "DE"),
                "ausland": sum(1 for i in ids if kunden[i]["land"] != "DE")}

    def eur(z: dict) -> float:
        b = float(z["nettobetrag"])
        return b if z["waehrung"] == "EUR" else b * kk[z["lieferdatum"][:4]][z["waehrung"]]

    letzte = {}
    for z in pos:
        if z["art"] == "Lieferung":
            letzte[z["kunde_id"]] = max(letzte.get(z["kunde_id"], ""), z["lieferdatum"])
    haendler = {i: kunden[i]["beliefert_endkunden"].split(";") for i in kunden if kunden[i]["ist_haendler"] == "ja"}
    endkunden = sorted({e for v in haendler.values() for e in v})
    k1003 = [z for z in pos if z["kunde_id"] == "K-1003"]
    j25 = [z for z in pos if z["lieferdatum"][:4] == "2025"]
    j26 = [z for z in pos if z["lieferdatum"][:4] == "2026"]
    u25 = sum(eur(z) for z in j25)
    u26 = sum(eur(z) for z in j26)
    l26 = sum(liter(z) for z in j26 if z["art"] != "Muster")
    nf26 = sum(liter(z) for z in j26 if z["art"] != "Muster" and z["auftragsart"] == "Nachfüllung")
    # Falle: Wachstumsraten der Segmente mitteln statt aus Summen rechnen
    seg = {}
    for z in j25 + j26:
        s = seg.setdefault(kunden[z["kunde_id"]]["segment"], [0.0, 0.0])
        s[0 if z["lieferdatum"][:4] == "2025" else 1] += eur(z)
    raten = [v[1] / v[0] - 1 for v in seg.values() if v[0]]
    return {
        "drill_0": {
            "D_lieferstellen": land(x["kunde_id"] for x in ls),
            "ruhende_kunden": {i: {"status": kunden[i]["status"], "letzte_lieferung": letzte.get(i)}
                               for i in kunden if kunden[i]["status"] != "aktiv"},
            "haendler_endkunden": {"haendler": haendler, "endkunden": endkunden,
                                   "alle_endkunden_schon_im_kundenstamm": all(e in kunden for e in endkunden)},
            "firmenzahl_unternehmen_md": "rund 1.400 Kunden in über 50 Ländern (Gesamtunternehmen, nicht nachzählbar)",
            "K-1003": {"lieferstellen": sum(1 for x in ls if x["kunde_id"] == "K-1003"),
                       "positionen": len(k1003),
                       "doppelimporte": sum(1 for z in auftraege if z["kunde_id"] == "K-1003") - len(k1003),
                       "erste_lieferung": min(z["lieferdatum"] for z in k1003),
                       "letzte_lieferung": max(z["lieferdatum"] for z in k1003)},
        },
        "drill_1": {
            "kacheln": {
                "kunden_aktiv_24_monate": land({z["kunde_id"] for z in pos if z["art"] == "Lieferung"
                                                and "2025-03-01" <= z["auftragsdatum"] <= "2027-02-28"}),
                "lieferstellen": len(ls),
                "absatz_2026_l": l26,
                "umsatz_2026_eur_konzernkurs": _r2(u26),
                "umsatz_2025_eur_konzernkurs": _r2(u25),
                "wachstum_umsatz_2026": round(u26 / u25 - 1, 4),
                "umsatz_2026_falsch_ohne_umrechnung": _r2(sum(float(z["nettobetrag"]) for z in j26)),
                "nachfuell_anteil_2026": round(nf26 / l26, 4),
            },
            "mittel_der_segment_wachstumsraten_2026_falsch": round(sum(raten) / len(raten), 4),
        },
    }


def main() -> int:
    fehler = pruefe_alles()
    for f in fehler:
        print("FEHLER:", f)
    # Regel 10: deterministisch (zwei Läufe, Vergleich mit den Dateien)
    import erzeuge_daten  # gleicher Ordner
    a = erzeuge_daten.erzeuge()
    if a != erzeuge_daten.erzeuge():
        fehler.append("Regel 10: zwei Läufe unterscheiden sich")
        print("FEHLER: Regel 10: zwei Läufe unterscheiden sich")
    for f in erzeuge_daten.pruefe_bytes(a):
        fehler.append(f)
        print("FEHLER: Regel 10:", f)
    print("Prüfung: %s" % ("grün" if not fehler else "%d Fehler" % len(fehler)))
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
