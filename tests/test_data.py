"""Prüft den fiktiven Übungsdatensatz (data/) gegen den Vertrag in docs/DATENMODELL.md.

Aufruf: python -m unittest discover -s tests -p 'test_data.py'
Nur Standardbibliothek (unittest), Python >= 3.9.
"""
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

_spec = importlib.util.spec_from_file_location("make_data", ROOT / "scripts" / "make_data.py")
md = importlib.util.module_from_spec(_spec)
sys.modules["make_data"] = md
_spec.loader.exec_module(md)

MONATE = {
    "Januar": 1, "Februar": 2, "März": 3, "April": 4, "Mai": 5, "Juni": 6, "Juli": 7,
    "August": 8, "September": 9, "Oktober": 10, "November": 11, "Dezember": 12,
}
DATUM_RE = re.compile(r"(\d{1,2})\. (%s) (\d{4})" % "|".join(MONATE))
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ISO_ZEIT_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$")

ANWENDUNGEN = [
    "tragbarer_feuerloescher", "fahrbarer_feuerloescher", "stationaere_anlage",
    "feuerwehrfahrzeug", "uebung_training", "lager_bestand",
]
MAIL_KOPF = ["id", "welle", "typ", "von", "betreff", "empfangen", "kunde_id", "anhaenge"]
MAIL_TYPEN = {"aufgabe", "verordnung", "berichtigung", "kundenanfrage", "intern"}


def lade(name):
    with open(DATA / name, encoding="utf-8") as fh:
        return json.load(fh)


def lese(pfad):
    return Path(pfad).read_text(encoding="utf-8")


def deutsche_daten(text):
    """Alle Daten der Form '1. März 2029' als ISO-Mengen."""
    out = []
    for tag, monat, jahr in DATUM_RE.findall(text):
        out.append("%s-%02d-%02d" % (jahr, MONATE[monat], int(tag)))
    return out


def artikel_abschnitte(text):
    """Artikelnummer -> Text des Artikels."""
    teile = re.split(r"^## Artikel (\d+) – .*$", text, flags=re.M)
    return {int(teile[i]): teile[i + 1] for i in range(1, len(teile), 2)}


def absaetze(artikel_text):
    """Absatznummer -> Text (Zeilen, die mit 'N. ' beginnen, bis zum nächsten Absatz)."""
    out = {}
    aktuell = None
    for zeile in artikel_text.split("\n"):
        m = re.match(r"^(\d+)\. (?!(?:%s) \d{4})" % "|".join(MONATE), zeile)
        if m:
            aktuell = int(m.group(1))
            out[aktuell] = zeile
        elif aktuell is not None:
            out[aktuell] += "\n" + zeile
    return out


def parse_artikelref(ref):
    m = re.match(r"^Art\. (\d+)(?: Abs\. (\d+))?(?: Nr\. (\d+))?$", ref)
    assert m, "Artikelverweis nicht lesbar: %s" % ref
    return int(m.group(1)), (int(m.group(2)) if m.group(2) else None), (int(m.group(3)) if m.group(3) else None)


def mails():
    return md.lade_mails(DATA / "eingang")


class DateiFormat(unittest.TestCase):
    def test_json_dateien_lf_utf8_ohne_bom(self):
        for name in ("welt.json", "regelwerk.json", "produkte.json", "kunden.json", "lieferungen.json"):
            roh = (DATA / name).read_bytes()
            self.assertFalse(roh.startswith(b"\xef\xbb\xbf"), name)
            self.assertNotIn(b"\r", roh, name)
            self.assertTrue(roh.endswith(b"\n"), name)
            roh.decode("utf-8")

    def test_texte_lf(self):
        for pfad in list((DATA / "eingang").glob("*.md")) + list((DATA / "regulation").glob("*.md")):
            self.assertNotIn(b"\r", pfad.read_bytes(), pfad.name)


class Determinismus(unittest.TestCase):
    def test_zweimal_erzeugen_identisch(self):
        self.assertEqual(md.build_all(), md.build_all())

    def test_eingecheckte_daten_sind_aktuell(self):
        for name, text in md.build_all().items():
            self.assertEqual((DATA / name).read_text(encoding="utf-8"), text,
                             "data/%s weicht ab: python scripts/make_data.py ausführen" % name)

    def test_loesung_deterministisch_und_ohne_dozentenordner(self):
        a = md.build_loesung_dateien()
        b = md.build_loesung_dateien()
        self.assertEqual(a, b)
        self.assertIn("loesung.json", a)
        self.assertIn("LOESUNG.md", a)


class Welt(unittest.TestCase):
    def test_welt(self):
        w = lade("welt.json")
        self.assertEqual(w["heute"], "2027-03-15")
        self.assertEqual(w["eingriffsfenster_stunden"], 24)
        self.assertIn("fiktiv", w["firma"].lower())

    def test_alle_fristen_nach_heute(self):
        w = lade("welt.json")
        r = lade("regelwerk.json")
        daten = [r["informationspflicht_bis"], r["inkrafttreten"]]
        for a in r["anwendungen"]:
            daten.extend(a[f] for f in ("inverkehrbringen_verbot_ab", "verwendung_verbot_ab",
                                        "bestandsmeldung_bis", "kennzeichnung_ab") if a[f])
        for x in r["ausnahmen"]:
            daten.append(x["befristet_bis"])
        for x in daten:
            self.assertGreater(x, w["heute"])


class Produkte(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = lade("produkte.json")
        cls.by_id = {p["id"]: p for p in cls.p}

    def test_anzahl_und_eindeutige_ids(self):
        self.assertTrue(22 <= len(self.p) <= 28, len(self.p))
        self.assertEqual(len(self.by_id), len(self.p))

    def test_felder_und_erlaubte_werte(self):
        felder = ["id", "name", "schaumart", "brandklassen", "einsatzbereiche", "basis", "pfas_wert",
                  "pfas_einheit", "fluorfrei_deklariert", "zumischrate_prozent", "sdb_version",
                  "sdb_datum", "tdb_version", "nachfolger_id", "status", "bemerkung"]
        for p in self.p:
            self.assertEqual(list(p.keys()), felder, p["id"])
            self.assertIn(p["schaumart"], md.SCHAUMARTEN)
            self.assertTrue(p["brandklassen"])
            self.assertTrue(set(p["brandklassen"]) <= set(md.BRANDKLASSEN))
            self.assertTrue(p["einsatzbereiche"])
            self.assertTrue(set(p["einsatzbereiche"]) <= set(md.EINSATZBEREICHE), p["id"])
            self.assertIn(p["basis"], md.BASEN)
            self.assertIn(p["pfas_einheit"], ("mg/l", "µg/l", None))
            self.assertEqual(p["pfas_wert"] is None, p["pfas_einheit"] is None, p["id"])
            self.assertIn(p["status"], ("aktiv", "auslaufend", "ruhend"))
            self.assertIsInstance(p["fluorfrei_deklariert"], bool)
            self.assertRegex(p["sdb_datum"], ISO_RE)
            self.assertLessEqual(p["sdb_datum"], "2027-03-15")
            self.assertRegex(p["sdb_version"], r"^\d+\.\d+$")
            self.assertRegex(p["tdb_version"], r"^\d+\.\d+$")

    def test_nachfolger_existieren(self):
        for p in self.p:
            if p["nachfolger_id"]:
                self.assertIn(p["nachfolger_id"], self.by_id, p["id"])
                self.assertNotEqual(p["nachfolger_id"], p["id"])

    def test_erfundene_namen(self):
        for p in self.p:
            n = p["name"].lower()
            for verboten in ("vapurex", "sthamer", "moussol", "sthamex"):
                self.assertNotIn(verboten, n, p["name"])

    def test_stolperstellen(self):
        def mg(p):
            if p["pfas_wert"] is None:
                return None
            return p["pfas_wert"] / 1000.0 if p["pfas_einheit"] == "µg/l" else float(p["pfas_wert"])

        grenz = lade("regelwerk.json")["grenzwert_mg_l"]
        werte = [mg(p) for p in self.p]
        self.assertIn(grenz, werte, "kein Produkt genau auf dem Grenzwert")
        self.assertTrue(any(w is not None and abs(w - 0.9) < 1e-9 for w in werte), "kein Produkt mit 0,9 mg/l")
        self.assertTrue(any(w is not None and abs(w - 1.1) < 1e-9 for w in werte), "kein Produkt mit 1,1 mg/l")
        self.assertTrue(any(p["pfas_einheit"] == "µg/l" and mg(p) <= grenz for p in self.p), "kein µg/l-Wert unter Grenzwert")
        self.assertTrue(any(p["pfas_einheit"] == "µg/l" and mg(p) > grenz for p in self.p), "kein µg/l-Wert über Grenzwert")
        self.assertTrue(any(p["pfas_wert"] is None and p["fluorfrei_deklariert"] for p in self.p), "kein fluorfrei ohne Messwert")
        self.assertTrue(any(p["fluorfrei_deklariert"] and mg(p) is not None and mg(p) > grenz for p in self.p),
                        "kein Widerspruch Deklaration/Messwert")
        # zwei Produkte mit sehr ähnlichen Namen (gleiche zwei ersten Wörter, nicht identisch)
        praefixe = {}
        for p in self.p:
            praefixe.setdefault(" ".join(p["name"].split()[:2]), []).append(p["name"])
        self.assertTrue(any(len(v) >= 2 for v in praefixe.values()), "keine ähnlichen Produktnamen")
        self.assertTrue(any(p["status"] == "auslaufend" and p["nachfolger_id"] is None for p in self.p),
                        "kein auslaufendes Produkt ohne Nachfolger")

    def test_loesung_stati(self):
        status = {}
        grenz = lade("regelwerk.json")["grenzwert_mg_l"]
        for p in self.p:
            status[p["id"]] = md.produkt_status(p, grenz)[0]
        self.assertEqual(status["P-114"], "nein")  # genau auf dem Grenzwert
        self.assertEqual(status["P-107"], "ja")    # 1,1
        self.assertEqual(status["P-116"], "nein")  # 800 µg/l
        self.assertEqual(status["P-117"], "ja")    # 1400 µg/l
        self.assertEqual(status["P-118"], "unklar")
        self.assertEqual(status["P-119"], "unklar")
        self.assertEqual(sorted(k for k, v in status.items() if v == "unklar"), ["P-118", "P-119"])


class Kunden(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.k = lade("kunden.json")
        cls.by_id = {k["id"]: k for k in cls.k}
        cls.r = lade("regelwerk.json")

    def test_anzahl_und_felder(self):
        self.assertTrue(28 <= len(self.k) <= 36, len(self.k))
        self.assertEqual(len(self.by_id), len(self.k))
        felder = ["id", "name", "segment", "land", "sprache", "ansprechpartner", "seveso", "key_account",
                  "ist_haendler", "beliefert_endkunden", "ausnahme_ids", "status", "bemerkung"]
        for k in self.k:
            self.assertEqual(list(k.keys()), felder, k["id"])
            self.assertEqual(list(k["ansprechpartner"].keys()), ["name", "rolle", "email"])
            self.assertIn(k["segment"], md.SEGMENTE)
            self.assertIn(k["land"], ("DE", "AT", "NL", "PL", "CH", "GB", "NO"))
            self.assertIn(k["sprache"], ("de", "en"))
            self.assertIn(k["status"], ("aktiv", "ruhend"))

    def test_email_domains(self):
        for k in self.k:
            domain = k["ansprechpartner"]["email"].split("@")[1]
            self.assertTrue(domain.endswith("example.com") or domain.endswith(".invalid"), k["id"])

    def test_referenzen(self):
        ausn = set(a["id"] for a in self.r["ausnahmen"])
        for k in self.k:
            for e in k["beliefert_endkunden"]:
                self.assertIn(e, self.by_id, k["id"])
                self.assertNotEqual(e, k["id"])
            for a in k["ausnahme_ids"]:
                self.assertIn(a, ausn)
            if k["ist_haendler"]:
                self.assertTrue(k["beliefert_endkunden"], k["id"])
            else:
                self.assertEqual(k["beliefert_endkunden"], [], k["id"])
            self.assertEqual(k["ist_haendler"], k["segment"] == "Händler", k["id"])

    def test_ausnahmen_passen_zum_segment(self):
        ausn = {a["id"]: a for a in self.r["ausnahmen"]}
        for k in self.k:
            for a in k["ausnahme_ids"]:
                self.assertIn(k["segment"], ausn[a]["gilt_fuer_segmente"], k["id"])

    def test_pflichtmerkmale(self):
        k = self.k
        self.assertGreaterEqual(sum(1 for x in k if x["ist_haendler"]), 2)
        self.assertGreaterEqual(sum(1 for x in k if x["segment"] == "Flughafen"), 2)
        flug = [x for x in k if x["segment"] == "Flughafen"]
        self.assertTrue(any(x["ausnahme_ids"] for x in flug), "kein Flughafen mit Ausnahme")
        self.assertTrue(any(not x["ausnahme_ids"] for x in flug), "kein Flughafen ohne Ausnahme")
        self.assertGreaterEqual(sum(1 for x in k if x["status"] == "ruhend"), 1)
        self.assertGreaterEqual(sum(1 for x in k if x["key_account"]), 2)
        self.assertGreaterEqual(sum(1 for x in k if x["seveso"]), 2)
        self.assertGreaterEqual(sum(1 for x in k if x["sprache"] == "en"), 2)
        ausserhalb = [x for x in k if x["land"] not in self.r["geltungsbereich_laender"]]
        self.assertGreaterEqual(len(ausserhalb), 3)
        self.assertTrue({"CH", "GB", "NO"} <= set(x["land"] for x in ausserhalb))
        for seg in md.SEGMENTE:
            self.assertTrue(any(x["segment"] == seg for x in k), seg)

    def test_aehnliche_namen(self):
        namen = [x["name"] for x in self.k]
        gefunden = 0
        for i, a in enumerate(namen):
            for b in namen[i + 1:]:
                wa, wb = set(a.lower().replace("(", " ").replace(")", " ").split()), set(b.lower().replace("(", " ").replace(")", " ").split())
                if len(wa & wb) >= 3:
                    gefunden += 1
        self.assertGreaterEqual(gefunden, 2, "weniger als zwei Paare mit sehr ähnlichen Namen")


class Lieferungen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.l = lade("lieferungen.json")
        cls.k = {k["id"]: k for k in lade("kunden.json")}
        cls.p = {p["id"]: p for p in lade("produkte.json")}

    def test_anzahl_und_integritaet(self):
        self.assertTrue(140 <= len(self.l) <= 200, len(self.l))
        self.assertEqual(len(set(x["id"] for x in self.l)), len(self.l))
        felder = ["id", "kunde_id", "produkt_id", "anwendung", "anlage", "menge_l", "letzte_lieferung"]
        for x in self.l:
            self.assertEqual(list(x.keys()), felder, x["id"])
            self.assertIn(x["kunde_id"], self.k)
            self.assertIn(x["produkt_id"], self.p)
            self.assertIn(x["anwendung"], ANWENDUNGEN)
            self.assertRegex(x["letzte_lieferung"], ISO_RE)
            self.assertLessEqual(x["letzte_lieferung"], "2027-03-15")
            self.assertGreater(x["menge_l"], 0)
            self.assertTrue(x["anlage"])

    def test_jeder_kunde_hat_lieferungen(self):
        mit = set(x["kunde_id"] for x in self.l)
        self.assertEqual(mit, set(self.k))

    def test_alle_anwendungen_kommen_vor(self):
        self.assertEqual(set(x["anwendung"] for x in self.l), set(ANWENDUNGEN))

    def test_ruhender_kunde_alte_lieferungen(self):
        for x in self.l:
            if self.k[x["kunde_id"]]["status"] == "ruhend":
                self.assertLess(x["letzte_lieferung"], "2025-09-30")

    def test_nicht_betroffene_lieferungen_gibt_es(self):
        grenz = lade("regelwerk.json")["grenzwert_mg_l"]
        stati = [md.produkt_status(self.p[x["produkt_id"]], grenz)[0] for x in self.l]
        for s in ("ja", "nein", "unklar"):
            self.assertIn(s, stati)

    def test_loesung_kunden_ohne_betroffene_lieferung(self):
        loesung = json.loads(md.build_loesung_dateien()["loesung.json"])
        nicht = [k["id"] for k in loesung["kunden"] if k["betroffenheit"] == "nicht betroffen"]
        self.assertIn("K-1026", nicht)
        self.assertIn("K-1008", nicht)


class Regelwerk(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = lade("regelwerk.json")
        cls.vo = lese(DATA / "regulation" / "vo-fiktiv-2026-9001.md")
        cls.b = lese(DATA / "regulation" / "berichtigung-1.md")
        cls.art = artikel_abschnitte(cls.vo)

    def test_kopfzeile_fiktiv(self):
        self.assertIn("FIKTIVER ÜBUNGSTEXT – kein geltendes Recht", self.vo)
        self.assertIn("FIKTIVER ÜBUNGSTEXT – kein geltendes Recht", self.b)
        self.assertIn("2026/9001", self.vo.split("\n")[0])

    def test_struktur_des_json(self):
        self.assertEqual(list(self.r.keys())[:8], ["id", "titel", "grenzwert_mg_l", "grenzwert_regel",
                                                    "geltungsbereich_laender", "anwendungen", "ausnahmen", "berichtigung"])
        self.assertEqual([a["id"] for a in self.r["anwendungen"]], ANWENDUNGEN)
        for a in self.r["anwendungen"]:
            self.assertEqual(list(a.keys()), ["id", "name", "artikel", "inverkehrbringen_verbot_ab", "verwendung_verbot_ab",
                                              "bestandsmeldung_bis", "kennzeichnung_ab"])
            for f in ("inverkehrbringen_verbot_ab", "verwendung_verbot_ab", "bestandsmeldung_bis", "kennzeichnung_ab"):
                if a[f] is not None:
                    self.assertRegex(a[f], ISO_RE)
        self.assertEqual(self.r["grenzwert_regel"], "mehr_als")
        self.assertEqual(self.r["grenzwert_mg_l"], 1.0)

    def test_artikel_vorhanden(self):
        self.assertEqual(sorted(self.art), list(range(1, 11)))

    def test_grenzwert_im_text(self):
        art3 = self.art[3]
        self.assertIn("1 mg/l", art3)
        self.assertIn("mehr als 1 mg/l", art3)
        self.assertIn("genau 1 mg/l", art3)
        self.assertIn("1 000 µg/l", art3)

    def test_geltungsbereich_im_text(self):
        abs1 = absaetze(self.art[1])
        for land in ("Deutschland", "Österreich", "Niederlande", "Polen"):
            self.assertIn(land, abs1[2])
        for land in ("Schweiz", "Vereinigten Königreich", "Norwegen"):
            self.assertIn(land, abs1[3])
        self.assertEqual(set(self.r["geltungsbereich_laender"]), {"DE", "AT", "NL", "PL"})

    def test_anwendungen_gegen_text(self):
        for a in self.r["anwendungen"]:
            n_art, n_abs, _ = parse_artikelref(a["artikel"])
            para = absaetze(self.art[n_art])[n_abs]
            if a["id"] == "lager_bestand":
                self.assertIn(a["name"], para, a["id"])  # Art. 6 ist Fließtext ohne Doppelpunkt
            else:
                self.assertIn(a["name"] + ":", para, a["id"])
            erwartet = set(x for x in (a["inverkehrbringen_verbot_ab"], a["verwendung_verbot_ab"]) if x)
            self.assertEqual(set(deutsche_daten(para)), erwartet, "%s: Daten in %s" % (a["id"], a["artikel"]))
            if a["verwendung_verbot_ab"] is None:
                self.assertNotIn("verwendet", para, a["id"])
            else:
                self.assertIn("nicht mehr verwendet", para, a["id"])

    def _liste_zeile(self, artikel_nr, abs_nr, name):
        para = absaetze(self.art[artikel_nr])[abs_nr]
        for zeile in para.split("\n"):
            if zeile.startswith("- " + name + ":"):
                return zeile
        self.fail("Zeile '%s' fehlt in Art. %s Abs. %s" % (name, artikel_nr, abs_nr))

    def test_kennzeichnung_und_meldung_gegen_text(self):
        for a in self.r["anwendungen"]:
            z5 = self._liste_zeile(5, 1, a["name"])
            self.assertEqual(deutsche_daten(z5), [a["kennzeichnung_ab"]], a["id"])
            z7 = self._liste_zeile(7, 1, a["name"])
            self.assertEqual(deutsche_daten(z7), [a["bestandsmeldung_bis"]], a["id"])

    def test_informationspflicht_inkrafttreten(self):
        p = absaetze(self.art[7])[3]
        self.assertEqual(deutsche_daten(p), [self.r["informationspflicht_bis"]])
        n_art, n_abs, _ = parse_artikelref(self.r["informationspflicht_artikel"])
        self.assertEqual((n_art, n_abs), (7, 3))
        self.assertIn(self.r["inkrafttreten"], deutsche_daten(self.art[10]))
        self.assertIn(self.r["veroeffentlicht"], deutsche_daten(self.vo))

    def test_ausnahmen_gegen_text(self):
        for x in self.r["ausnahmen"]:
            n_art, n_abs, _ = parse_artikelref(x["artikel"])
            para = absaetze(self.art[n_art])[n_abs]
            self.assertIn(x["befristet_bis"], deutsche_daten(para), x["id"])
        flug = absaetze(self.art[8])[2]
        self.assertIn("Flughäfen", flug)
        self.assertIn("Artikel 4 Absatz 4", flug)
        umst = absaetze(self.art[8])[3]
        self.assertIn("Artikel 4 Absatz 3", umst)
        for seg in ("Industrie", "Montanindustrie", "Schifffahrt und Werft"):
            self.assertIn(seg, umst)
        by_id = {x["id"]: x for x in self.r["ausnahmen"]}
        self.assertEqual(by_id["AUSN-FLUGHAFEN"]["gilt_fuer_anwendungen"], ["feuerwehrfahrzeug"])
        self.assertEqual(by_id["AUSN-UMSTELLUNGSPLAN"]["gilt_fuer_anwendungen"], ["stationaere_anlage"])

    def test_berichtigung_gegen_text(self):
        b = self.r["berichtigung"]
        by_id = {a["id"]: a for a in self.r["anwendungen"]}
        self.assertEqual(len(b["aenderungen"]), 1)
        for aend in b["aenderungen"]:
            a = by_id[aend["anwendung"]]
            self.assertEqual(a[aend["feld"]], aend["alt"], "alt stimmt nicht mit der Ursprungsfassung überein")
            self.assertGreater(aend["neu"], aend["alt"])
            self.assertIn(aend["alt"], deutsche_daten(self.b))
            self.assertIn(aend["neu"], deutsche_daten(self.b))
            n_art, n_abs, _ = parse_artikelref(aend["artikel"])
            self.assertIn("Artikel %d Absatz %d" % (n_art, n_abs), self.b)
            # die Verordnung nennt weiterhin das alte Datum (Berichtigung ersetzt es)
            self.assertIn(aend["alt"], deutsche_daten(absaetze(self.art[n_art])[n_abs]))
            # Reihenfolge bleibt sinnvoll: Inverkehrbringen vor Verwendungsverbot
            self.assertLess(aend["neu"], a["verwendung_verbot_ab"])
        for k in b["klarstellungen"]:
            n_art, n_abs, n_nr = parse_artikelref(k["artikel"])
            self.assertIn("Artikel %d Nummer %d" % (n_art, n_nr), self.b)
            self.assertIn(k["text"], self.b.replace("\n", " "))
        self.assertIn(b["veroeffentlicht"], deutsche_daten(self.b))


class Eingang(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = mails()
        cls.kunden = {k["id"]: k for k in lade("kunden.json")}
        cls.by_email = {k["ansprechpartner"]["email"]: k for k in cls.kunden.values()}
        cls.produkte = lade("produkte.json")
        cls.lief = lade("lieferungen.json")

    def test_kopfzeilen_vollstaendig(self):
        self.assertTrue(len(self.m) >= 14)
        ids = set()
        for m in self.m:
            for feld in MAIL_KOPF:
                self.assertIn(feld, m, "%s: %s fehlt" % (m["_datei"], feld))
            for feld in ("id", "welle", "typ", "von", "betreff", "empfangen"):
                self.assertTrue(m[feld], "%s: %s leer" % (m["_datei"], feld))
            self.assertRegex(m["id"], r"^MSG-\d-\d{2}$")
            self.assertTrue(m["_datei"].startswith("%s-%s-" % (m["id"].split("-")[1], m["id"].split("-")[2])), m["_datei"])
            self.assertEqual(int(m["welle"]), int(m["id"].split("-")[1]))
            self.assertIn(m["typ"], MAIL_TYPEN)
            self.assertRegex(m["empfangen"], ISO_ZEIT_RE)
            self.assertTrue(m["empfangen"].startswith("2027-03-15"), m["_datei"])
            self.assertRegex(m["von"], r"^.+ <[^<>@\s]+@[^<>\s]+>$", m["_datei"])
            domain = m["von"].split("@")[1].rstrip(">")
            self.assertTrue(domain.endswith("example.com") or domain.endswith(".invalid"), m["_datei"])
            self.assertTrue(m["_text"].strip(), m["_datei"])
            ids.add(m["id"])
        self.assertEqual(len(ids), len(self.m))

    def test_wellen(self):
        zaehler = {}
        for m in self.m:
            zaehler[int(m["welle"])] = zaehler.get(int(m["welle"]), 0) + 1
        self.assertEqual(set(zaehler), {1, 2, 3, 4})
        self.assertGreaterEqual(zaehler[1], 2)
        self.assertGreaterEqual(zaehler[2], 4)
        self.assertGreaterEqual(zaehler[3], 5)
        self.assertGreaterEqual(zaehler[4], 1)
        zeiten = [(int(m["welle"]), m["empfangen"]) for m in self.m]
        self.assertEqual(zeiten, sorted(zeiten), "Eingangszeiten müssen mit den Wellen wachsen")

    def test_runden_brauchen_keinen_code(self):
        """Seit dem 26.11.2026: Neue Mails kommen mit einem Klick auf „Postfach abrufen“, ohne Code vom Dozenten."""
        with open(DATA / "wellen.json", encoding="utf-8") as fh:
            cfg = json.load(fh)
        self.assertEqual(set(cfg), {"1", "2", "3", "4"})
        for nr, eintrag in cfg.items():
            self.assertIsNone(eintrag.get("code_sha256"), "Runde %s verlangt einen Code" % nr)

    def test_anhaenge_existieren(self):
        for m in self.m:
            for a in [x.strip() for x in m["anhaenge"].split(",") if x.strip()]:
                self.assertTrue((DATA / a).is_file(), "%s: Anhang %s fehlt" % (m["_datei"], a))
        w1 = [m for m in self.m if m["welle"] == "1" and m["typ"] == "aufgabe"]
        self.assertEqual(len(w1), 1)
        self.assertIn("vo-fiktiv-2026-9001.md", w1[0]["anhaenge"])
        w4 = [m for m in self.m if m["typ"] == "berichtigung"]
        self.assertEqual(len(w4), 1)
        self.assertIn("berichtigung-1.md", w4[0]["anhaenge"])

    def test_kunden_bezug(self):
        for m in self.m:
            kid = m["kunde_id"]
            if kid:
                self.assertIn(kid, self.kunden, m["_datei"])
                self.assertEqual(self.by_email.get(m["von"].split("<")[1].rstrip(">")), self.kunden[kid], m["_datei"])
                nummern = set(re.findall(r"K-\d{4}", m["_text"]))
                self.assertTrue(nummern <= {kid}, "%s: nennt fremde Kundennummer %s" % (m["_datei"], nummern))
            else:
                self.assertEqual(re.findall(r"K-\d{4}", m["_text"]), [], m["_datei"])

    def test_genannte_produkte_sind_geliefert(self):
        geliefert = {}
        for l in self.lief:
            geliefert.setdefault(l["kunde_id"], set()).add(l["produkt_id"])
        namen = {p["id"]: p["name"] for p in self.produkte}
        for m in self.m:
            if m["typ"] != "kundenanfrage":
                continue
            email = m["von"].split("<")[1].rstrip(">")
            kunde = self.by_email[email]
            text = " ".join((m["_text"] + " " + m["betreff"]).split())
            for pid, name in namen.items():
                if name in text:
                    self.assertIn(pid, geliefert[kunde["id"]], "%s nennt %s, nicht an %s geliefert" % (m["_datei"], name, kunde["id"]))

    def test_welle2_deckt_die_faelle_ab(self):
        w2 = [m for m in self.m if m["welle"] == "2"]
        kunden = [self.kunden[m["kunde_id"]] for m in w2]
        self.assertTrue(any(k["ist_haendler"] for k in kunden), "keine Händlermail")
        self.assertTrue(any(k["land"] not in ("DE", "AT", "NL", "PL") for k in kunden), "keine Mail von außerhalb")
        self.assertTrue(any(k["ausnahme_ids"] for k in kunden), "keine Mail mit Ausnahme")
        self.assertGreaterEqual(sum(1 for k in kunden if not k["ist_haendler"] and k["land"] in ("DE", "AT", "NL", "PL")
                                    and not k["ausnahme_ids"]), 2, "weniger als zwei klare Fälle")

    def test_injection_mail(self):
        inj = [m for m in self.m if "Ignoriere alle bisherigen Regeln" in " ".join(m["_text"].split())]
        self.assertEqual(len(inj), 1)
        self.assertEqual(inj[0]["welle"], "3")
        self.assertEqual(inj[0]["kunde_id"], "")
        # Absender lässt sich nur über die Domain zuordnen, und zwar eindeutig
        email = inj[0]["von"].split("<")[1].rstrip(">")
        self.assertEqual(self.by_email[email]["id"], "K-1030")
        text = " ".join(inj[0]["_text"].split())
        self.assertIn("Hafenchemie Nord", text)
        self.assertNotIn("Hafenchemie Nord Logistik", text)  # mehrdeutig: K-1001 oder K-1030

    def test_englische_mails(self):
        en = [m for m in self.m if m["kunde_id"] and self.kunden[m["kunde_id"]]["sprache"] == "en"]
        self.assertGreaterEqual(len(en), 2)
        for m in en:
            self.assertTrue("regards" in m["_text"] or "Regards" in m["_text"], m["_datei"])

    def test_loesungsschluessel_deckt_alle_mails_ab(self):
        l = json.loads(md.build_loesung_dateien()["loesung.json"])
        ids = {e["id"] for e in l["eingang"]}
        self.assertEqual(ids, {m["id"] for m in self.m})
        for e in l["eingang"]:
            self.assertTrue(e.get("behandlung"), e["id"])
            self.assertTrue(e.get("stolperstelle"), e["id"])
            self.assertTrue(e.get("kontrollstufe"), e["id"])
        self.assertTrue(l["berichtigung"]["falsche_mails_kunden"])
        self.assertTrue(all(i in ids for i in l["berichtigung"]["falsche_mails_eingang"]))


class Loesung(unittest.TestCase):
    def test_kontrollstufen_und_ausnahmen(self):
        l = json.loads(md.build_loesung_dateien()["loesung.json"])
        k = {x["id"]: x for x in l["kunden"]}
        self.assertEqual(k["K-1010"]["kontrollstufe_info_mail"], "eingriffsfenster")
        self.assertEqual(k["K-1015"]["kontrollstufe_info_mail"], "pflichtfreigabe")
        self.assertEqual(k["K-1023"]["kontrollstufe_info_mail"], "pflichtfreigabe")
        self.assertEqual(k["K-1029"]["kontrollstufe_info_mail"], "pflichtfreigabe")
        self.assertEqual(k["K-1021"]["kontrollstufe_info_mail"], "pflichtfreigabe")
        self.assertEqual(k["K-1030"]["betroffenheit"], "unklar")
        wirk = [w["ausnahme"] for w in k["K-1015"]["ausnahmen_wirkung"]]
        self.assertEqual(set(wirk), {"AUSN-FLUGHAFEN"})
        # Ausnahme gilt nur für Fahrzeuge, nicht für die Hangar-Anlage
        self.assertTrue(all(w["anwendung"] == "feuerwehrfahrzeug" for w in k["K-1015"]["ausnahmen_wirkung"]))
        self.assertEqual(k["K-1016"]["ausnahmen_wirkung"], [])
        self.assertEqual(k["K-1027"]["fruehstes_verbot"]["datum"], "2027-07-01")

    def test_markdown_enthaelt_abschnitte(self):
        txt = md.build_loesung_dateien()["LOESUNG.md"]
        for kopf in ("## Regeln", "## Produkte", "## Kunden", "## Eingangsnachrichten", "## Berichtigung"):
            self.assertIn(kopf, txt)


if __name__ == "__main__":
    unittest.main()
