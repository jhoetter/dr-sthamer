#!/usr/bin/env python3
"""Konsistenzprüfungen für die Daten und Texte von Tag 1 (Regeln 1-10 aus dem Plan, 11-13 Finanzdaten).

Nur Standardbibliothek, Python >= 3.9. Bewusst kein test_*.py, damit die
Prüfszenarien von Tag 2 nichts davon einsammeln.

Aufruf:  python werkzeuge/pruefe_daten.py
"""
from __future__ import annotations

import csv
import json
import re
import sys
from datetime import date
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

# Spoiler-Schutz 2.4
FALLTRAEGER_GESPERRT = ["K-1007", "K-1010", "K-1011", "K-1014", "K-1015", "K-1017", "K-1021", "K-1023",
                        "K-1026", "K-1027", "K-1001", "K-1030", "K-1008", "K-1009", "K-1016"]
PRODUKTE_GESPERRT = ["P-114", "P-115", "P-116", "P-117", "P-118", "P-119", "P-107", "P-120"]
TEXT_ORDNER = ["akten", "angebotseingang", "notizbuch"]
# Regel 6: Begriffe aus Tag 2
VO_BEGRIFFE = [r"Grenzwert", r"mg/l", r"µg/l", r"Verordnung \(EU\)", r"Berichtigung"]
# Regel 9 (Nachtrag 21.11.2026): «Sthamer» ist erlaubt
NAMEN_GESPERRT = r"hsg|gallen|unisg|itmp|pfefferminz|minzia|holzweid"
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
    kontakte = lies_csv("kontakte.csv", daten) if (daten / "kontakte.csv").exists() else []
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
                                 ("kontakte", kontakte, "kunde_id", None),
                                 ("preislisten", preise, None, "produkt_id")]:
        for z in zeilen:
            if kf and not k_ok(z[kf]):
                fehler.append("Regel 1: %s nennt unbekannten Kunden %s" % (name, z[kf]))
            if pf and z[pf] not in pq:
                fehler.append("Regel 1: %s nennt unbekanntes Produkt %s" % (name, z[pf]))
    for p in produkte:
        if p["nachfolger_id"] and p["nachfolger_id"] not in pq:
            fehler.append("Regel 1: Nachfolger %s unbekannt" % p["nachfolger_id"])
    for z in auftraege:
        if z["lieferstelle_id"] not in ls_von:
            fehler.append("Regel 1: Lieferstelle %s unbekannt" % z["lieferstelle_id"])
        elif ls_von[z["lieferstelle_id"]]["kunde_id"] != z["kunde_id"]:
            fehler.append("Regel 1: Lieferstelle %s gehört nicht zu %s" % (z["lieferstelle_id"], z["kunde_id"]))

    # Regel 2: letzte Lieferung je Lieferstelle x Produkt x Anwendung
    anlage = {(x["kunde_id"], x["anlage"]): x["lieferstelle_id"] for x in ls}
    letzte = {}
    for z in auftraege:
        if z["art"] in ("Lieferung", "Muster"):
            s = (z["lieferstelle_id"], z["produkt_id"], z["anwendung"])
            letzte[s] = max(letzte.get(s, ""), z["lieferdatum"])
    for l in lq:
        s = (anlage[(l["kunde_id"], l["anlage"])], l["produkt_id"], l["anwendung"])
        if letzte.get(s) != l["letzte_lieferung"]:
            fehler.append("Regel 2: %s letzte Lieferung %s statt %s" % (l["id"], letzte.get(s), l["letzte_lieferung"]))

    # Regel 3: K-1029 ruhend
    for z in auftraege:
        if z["kunde_id"] == "K-1029" and z["auftragsdatum"] > "2025-09-30":
            fehler.append("Regel 3: K-1029 hat Auftrag am %s" % z["auftragsdatum"])

    # Regel 4: P-2xx nicht vor Einführung; P-121 ohne Nachfolger
    for z in auftraege:
        if z["lieferdatum"] < prod[z["produkt_id"]]["eingefuehrt_am"]:
            fehler.append("Regel 4: %s vor Einführung geliefert (%s)" % (z["produkt_id"], z["lieferdatum"]))
    if prod["P-121"]["nachfolger_id"]:
        fehler.append("Regel 4: P-121 hat einen Nachfolger")

    # Regel 5: Datumsgrenzen
    for name, zeilen, felder in [("auftraege", auftraege, ["auftragsdatum", "lieferdatum"]),
                                 ("lieferstellen", ls, ["letzte_lieferung", "datenaufnahme_am"]),
                                 ("reklamationen", rekl, ["eingang"]), ("kontakte", kontakte, ["datum"]),
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
            kopf = f.readline()
        for feld in ("pfas_wert", "pfas_einheit", "bemerkung", "seveso", "sdb_", "tdb_"):
            if feld in kopf:
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
            if re.search(r"\b%s\b" % pid, t) or pq[pid]["name"] in t:
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

    # Reklamationen: Produkt vorher an den Kunden geliefert; Raffinerie-Nummern wie in der Akte
    geliefert = {}
    for z in auftraege:
        if z["art"] in ("Lieferung", "Muster"):
            s = (z["kunde_id"], z["produkt_id"])
            geliefert[s] = min(geliefert.get(s, "9999"), z["lieferdatum"])
    for r in rekl:
        if geliefert.get((r["kunde_id"], r["produkt_id"]), "9999") >= r["eingang"]:
            fehler.append("Reklamation %s: Produkt vorher nicht geliefert" % r["rekl_id"])
    raff = {r["rekl_id"]: r for r in rekl if r["kunde_id"] == "K-1003"}
    if rekl and not ("R-2026-008" in raff and raff["R-2026-008"]["eingang"] == "2026-05-08"
                     and "R-2026-009" in raff and raff["R-2026-009"]["eingang"] == "2026-05-19"):
        fehler.append("Reklamationen: Raffinerie nicht als R-2026-008 (08.05.) und R-2026-009 (19.05.)")

    # Kontakte gegen Akte (nur wenn der Ordner schon Dokumente enthält)
    akte = TAG1 / "akten" / "K-1003 Raffinerie Kuestenmark"
    if akte.exists() and kontakte:
        vorhanden = {p.name for p in akte.iterdir() if p.is_file()}
        geplant = {k["dokument"] for k in kontakte if k["dokument"]}
        for d in sorted(vorhanden - geplant):
            fehler.append("Akte: %s fehlt in kontakte.csv" % d)

    # Regeln 11-13: Finanzdaten
    fehler += pruefe_finanzen(daten)
    return fehler


# --------------------------------------------------------------------------
# Finanzdaten (Drill 2): Kennzahlen nach kennzahlen.json, Regeln 11-13
# --------------------------------------------------------------------------

FINANZ_DATEIEN = ["herstellkosten.csv", "fracht.csv", "kurse.csv", "budget_2026.csv"]


def _r2(x: float) -> float:
    return round(x + 0.0, 2)


def finanzen(daten: Path = DATEN) -> dict:
    """Deckungsbeitrag, Plan-Ist-Brücke, Fremdwährung und Rabatte nach den Definitionen in kennzahlen.json."""
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    linie = {p["id"]: p["produktlinie"] for p in lies_csv("produkte.csv", daten)}
    pos = eindeutig(lies_csv("auftraege.csv", daten))
    hk = {(h["produkt_id"], h["jahr"]): float(h["rohstoff_eur_l"]) + float(h["fertigung_eur_l"])
          for h in lies_csv("herstellkosten.csv", daten)}
    fracht = {f["auftrag_id"]: float(f["frachtkosten_eur"]) for f in lies_csv("fracht.csv", daten)}
    kurse = {(k["monat"], k["waehrung"]): k for k in lies_csv("kurse.csv", daten)}
    budget = lies_csv("budget_2026.csv", daten)
    kk = json.loads((daten / "kennzahlen.json").read_text(encoding="utf-8"))["konzernkurse"]["kurse"]
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

    # (a) Deckungsbeitrag je Produktlinie, Segment, Kunde (Konzernkurs)
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
                      "db_vor_fracht_marge": round((um - herst) / um, 4) if um else None}
        return aus

    db = {}
    for j in ("2025", "2026"):
        db[j] = {
            "produktlinie": db_tabelle(j, lambda z: linie[z["produkt_id"]], False),
            "produktlinie_ohne_notfall": db_tabelle(j, lambda z: linie[z["produkt_id"]], True),
            "segment": db_tabelle(j, lambda z: kunden[z["kunde_id"]]["segment"], False),
            "kunde": db_tabelle(j, lambda z: z["kunde_id"], False),
            "gesamt": db_tabelle(j, lambda z: "gesamt", False)["gesamt"],
        }

    # (b) Plan-Ist-Brücke 2026
    plan = {}
    for b in budget:
        c = (b["produktlinie"], b["segment"])
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
        c = (linie[z["produkt_id"]], kunden[z["kunde_id"]]["segment"])
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
    ff_plan = sum(p[0] for c, p in plan.items() if c[0] == "fluorfrei")
    ff_ist = sum(a[0] for c, a in ist.items() if c[0] == "fluorfrei")
    bruecke = {
        "methode": "Zellen Produktlinie x Segment; siehe kennzahlen.json plan_ist_bruecke",
        "plan_liter": mp, "ist_liter_ohne_notfall": mi, "notfall_liter": notfall["liter"],
        "fluorfrei_anteil_plan": round(ff_plan / mp, 4), "fluorfrei_anteil_ist_ohne_notfall": round(ff_ist / mi, 4),
        "db_marge_plan": round(dp / up, 4),
        "db_marge_ist": round(db_bruecke["ist"] / umsatz_bruecke["ist"], 4),
        "db_marge_ist_ohne_notfall": round((ui_ist - ki) / ui_ist, 4),
        "umsatz": umsatz_bruecke, "deckungsbeitrag": db_bruecke, "zellen_ohne_plan": ohne_plan,
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

    # (c) Fremdwährung je Währung 2026 und Rabattquote 2025/2026
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
    produkte = {p["id"]: p for p in lies_csv("produkte.csv", daten)}
    pos = eindeutig(lies_csv("auftraege.csv", daten))
    hk = lies_csv("herstellkosten.csv", daten)
    fr = lies_csv("fracht.csv", daten)
    kurse = lies_csv("kurse.csv", daten)
    budget = lies_csv("budget_2026.csv", daten)
    kk = json.loads((daten / "kennzahlen.json").read_text(encoding="utf-8"))["konzernkurse"]["kurse"]

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
    for b in budget:
        if abs(round(int(b["menge_l"]) * float(b["preis_eur_l"]), 2) - float(b["umsatz_eur"])) > 0.005:
            fehler.append("Regel 11: Budget %s %s %s: Umsatz passt nicht" % (b["monat"], b["produktlinie"], b["segment"]))
        c = (b["produktlinie"], b["segment"])
        if preis_zelle.setdefault(c, b["preis_eur_l"]) != b["preis_eur_l"]:
            fehler.append("Regel 11: Budget-Preis je Liter schwankt in %s|%s" % c)
        if b["produktlinie"] not in ("fluorhaltig", "fluorfrei", "offen") or b["monat"][:4] != "2026":
            fehler.append("Regel 11: Budgetzeile unzulässig: %s" % b)

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
        dl = f["deckungsbeitrag"][j]["produktlinie_ohne_notfall"]
        if not dl["fluorfrei"]["db_marge"] + 0.15 < dl["fluorhaltig"]["db_marge"]:
            fehler.append("Regel 13: DB-Marge fluorfrei %s nicht klar unter fluorhaltig" % j)
    ub, dbb = pi["umsatz"], pi["deckungsbeitrag"]
    if not (ub["mengeneffekt"] < -100000 and pi["ist_liter_ohne_notfall"] < pi["plan_liter"]):
        fehler.append("Regel 13: keine klare Mengenlücke Plan-Ist 2026")
    if not (dbb["preiseffekt"] > 2000 and dbb["mixeffekt"] > 2000):
        fehler.append("Regel 13: Preis- und Mixeffekt im Deckungsbeitrag nicht beide positiv")
    if not (dbb["preiseffekt"] + dbb["mixeffekt"] < -dbb["mengeneffekt"]):
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
    if produkte["P-203"]["produktlinie"] != "fluorfrei":
        fehler.append("Regel 13: P-203 nicht fluorfrei")
    return fehler


def warnungen_akte(daten: Path = DATEN) -> list:
    """Geplante Akten-Dokumente, die noch nicht geschrieben sind (kein Fehler)."""
    akte = TAG1 / "akten" / "K-1003 Raffinerie Kuestenmark"
    if not akte.exists() or not (daten / "kontakte.csv").exists():
        return []
    vorhanden = {p.name for p in akte.iterdir() if p.is_file()}
    return sorted({k["dokument"] for k in lies_csv("kontakte.csv", daten) if k["dokument"]} - vorhanden)


# --------------------------------------------------------------------------
# Sollwerte (nur für das Lecture-Repo, über erzeuge_daten.py --sollwerte)
# --------------------------------------------------------------------------


def anteile(auftraege: list, produkte: dict, gruppe=None) -> dict:
    """Fluorfrei-Anteil nach Definition je (Jahr[, Gruppe])."""
    summen = {}
    for z in eindeutig(auftraege):
        if z["art"] == "Muster":
            continue
        jahr = z["lieferdatum"][:4]
        s = (jahr,) if gruppe is None else (jahr, gruppe(z))
        ff, alle, n = summen.get(s, (0, 0, 0))
        lt = liter(z)
        if produkte[z["produkt_id"]]["produktlinie"] == "fluorfrei":
            ff += lt
        summen[s] = (ff, alle + lt, n + 1)
    return {"|".join(s): {"fluorfrei_l": v[0], "alle_l": v[1], "positionen": v[2],
                          "anteil": round(v[0] / v[1], 4) if v[1] else None} for s, v in sorted(summen.items())}


def sollwerte(daten: Path = DATEN) -> dict:
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    produkte = {p["id"]: p for p in lies_csv("produkte.csv", daten)}
    ls = lies_csv("lieferstellen.csv", daten)
    auftraege = lies_csv("auftraege.csv", daten)
    rekl = lies_csv("reklamationen.csv", daten)
    roh = len(auftraege)
    ohne_dup = eindeutig(auftraege)
    seit = "2025-03-01"
    b = {k["kunde_id"] for k in ohne_dup if k["art"] == "Lieferung" and k["auftragsdatum"] >= seit}
    stat = [x for x in ls if x["anwendung"] == "stationaere_anlage"]
    return {
        "hinweis": "Sollwerte Tag 1, erzeugt aus tag1/daten. Nicht ins Teilnehmer-Repo.",
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
                      "erp_alt_ibc_ohne_liter": sum(1 for z in ohne_dup if z["menge_l"] == "")},
        "fluorfrei_anteil_jahr": anteile(auftraege, produkte),
        "fluorfrei_anteil_anwendung": anteile(auftraege, produkte, lambda z: z["anwendung"]),
        "fluorfrei_anteil_segment": anteile(auftraege, produkte, lambda z: kunden[z["kunde_id"]]["segment"]),
        "fluorfrei_anteil_vertriebsweg": anteile(auftraege, produkte, lambda z: z["vertriebsweg"]),
        "industrie_stationaer_vs_rest": anteile(
            [z for z in auftraege if kunden[z["kunde_id"]]["segment"] == "Industrie"], produkte,
            lambda z: "stationaer" if z["anwendung"] == "stationaere_anlage" else "rest"),
        "datenaufnahme_stationaer": {"anlagen": len(stat),
                                     "mit_datenaufnahme": sum(1 for x in stat if x["datenaufnahme_am"])},
        "reklamationen_probeumstellung": {
            "2026_bis_12_06": sum(1 for r in rekl if r["kategorie"] == "Probeumstellung"
                                  and "2026-01-01" <= r["eingang"] <= "2026-06-12"),
            "2026_gesamt": sum(1 for r in rekl if r["kategorie"] == "Probeumstellung" and r["eingang"][:4] == "2026"),
        },
        "finanzen": finanzen(daten),
        **sollwerte_drills(daten),
    }


def sollwerte_drills(daten: Path = DATEN) -> dict:
    """Zusätzliche Sollwerte für Drill 0 (Kundenzählweisen) und Drill 1 (Kacheln, Ampel, Nachhaken, Fallen)."""
    kunden = {k["id"]: k for k in lies_csv("kunden.csv", daten)}
    produkte = {p["id"]: p for p in lies_csv("produkte.csv", daten)}
    ls = lies_csv("lieferstellen.csv", daten)
    auftraege = lies_csv("auftraege.csv", daten)
    pos = eindeutig(auftraege)
    kk = json.loads((daten / "kennzahlen.json").read_text(encoding="utf-8"))["konzernkurse"]["kurse"]

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
    j26 = [z for z in pos if z["lieferdatum"][:4] == "2026"]
    j26_ohne = [z for z in j26 if z["vertriebsweg"] != "Notfallservice"]

    def fluorhaltig_ampel(zeilen) -> dict:
        s = {}
        for z in zeilen:
            if z["art"] == "Muster":
                continue
            g = "%s|%s" % (kunden[z["kunde_id"]]["segment"], kunden[z["kunde_id"]]["land"])
            a = s.setdefault(g, [0, 0, 0])
            lt = liter(z)
            a[0] += lt if produkte[z["produkt_id"]]["produktlinie"] == "fluorhaltig" else 0
            a[1] += lt
            a[2] += 1
        aus = {}
        for g in sorted(s):
            fh, alle, n = s[g]
            q = fh / alle if alle else None
            farbe = "Lücke" if n < 20 else ("rot" if q > 0.5 else "gelb" if q >= 0.2 else "grün")
            aus[g] = {"fluorhaltig_l": fh, "alle_l": alle, "positionen": n,
                      "anteil_fluorhaltig": round(q, 4) if q is not None else None, "ampel": farbe}
        return aus

    seg = anteile(j26, produkte, lambda z: kunden[z["kunde_id"]]["segment"])
    quoten = [v["anteil"] for v in seg.values() if v["anteil"] is not None]
    notfall = [z for z in pos if z["vertriebsweg"] == "Notfallservice"]
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
                "absatz_2026_l": sum(liter(z) for z in j26 if z["art"] != "Muster"),
                "umsatz_2026_eur_konzernkurs": _r2(sum(eur(z) for z in j26)),
                "umsatz_2026_falsch_ohne_umrechnung": _r2(sum(float(z["nettobetrag"]) for z in j26)),
                "fluorfrei_anteil_2026": anteile(j26, produkte)["2026"],
                "fluorfrei_anteil_2026_ohne_notfall": anteile(j26_ohne, produkte)["2026"],
            },
            "anwendung_2026_ohne_notfall": anteile(j26_ohne, produkte, lambda z: z["anwendung"]),
            "nachhak_2026": anteile(j26, produkte, lambda z: ("Industrie" if kunden[z["kunde_id"]]["segment"] == "Industrie"
                                                              else "andere") + ("|stationaer" if z["anwendung"] == "stationaere_anlage"
                                                                                else "|rest")),
            "ampel_segment_land_2026": fluorhaltig_ampel(j26),
            "mittel_der_segmentquoten_2026_falsch": round(sum(quoten) / len(quoten), 4),
            "notfall_positionen": [{"lieferdatum": z["lieferdatum"], "kunde_id": z["kunde_id"], "liter": liter(z),
                                    "nettobetrag": float(z["nettobetrag"])} for z in notfall],
        },
    }


def main() -> int:
    fehler = pruefe_alles()
    for f in fehler:
        print("FEHLER:", f)
    for w in warnungen_akte():
        print("Hinweis: Akten-Dokument noch nicht vorhanden:", w)
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
