import unittest

from tests.helpers import WeltTest
from sthamer_sys import domain, kontrollen, mcp_server
from sthamer_sys.store import transaktion, zustand_setzen
from sthamer_sys.paths import outbox_dir


def setze_welle(n):
    with transaktion() as conn:
        zustand_setzen(conn, "welle", str(n))


class StufenRegelTest(unittest.TestCase):
    def test_schlichter_kunde_ohne_rechtsaussage_bekommt_das_fenster(self):
        k = {"seveso": False, "key_account": False, "segment": "Industrie", "ist_haendler": False, "status": "aktiv", "land": "DE"}
        self.assertEqual(kontrollen.stufe_fuer(k, False, True, ["DE"]), ("eingriffsfenster", []))

    def test_jeder_grund_reicht_fuer_pflichtfreigabe(self):
        basis = {"seveso": False, "key_account": False, "segment": "Industrie", "ist_haendler": False, "status": "aktiv", "land": "DE"}
        faelle = [dict(basis, seveso=True), dict(basis, key_account=True), dict(basis, segment="Flughafen"),
                  dict(basis, ist_haendler=True), dict(basis, status="ruhend"), dict(basis, land="CH"),
                  dict(basis, ausnahme_ids=["AUSN-X"])]
        for k in faelle:
            stufe, gruende = kontrollen.stufe_fuer(k, False, True, ["DE"])
            self.assertEqual(stufe, "pflichtfreigabe", k)
            self.assertTrue(gruende)
        self.assertEqual(kontrollen.stufe_fuer(basis, True, True, ["DE"])[0], "pflichtfreigabe")
        self.assertEqual(kontrollen.stufe_fuer(basis, False, False, ["DE"])[0], "pflichtfreigabe")
        self.assertEqual(kontrollen.stufe_fuer(None, False, True, ["DE"])[0], "eingriffsfenster")  # interne Adresse


class FlussTest(WeltTest):
    def fall_und_entwurf(self, msg="MSG-1-02", an="e.muster@mueller.example.com"):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen(msg, akteur="claude")["fall_id"]
        return fid, domain.entwurf_anlegen(fid, an, "Antwort", "Guten Tag", [], "claude")["entwurf_id"]

    def test_vor_runde_2_gibt_es_kein_einreichen_und_der_mensch_sendet_direkt(self):
        fid, eid = self.fall_und_entwurf()
        with self.assertRaises(domain.FachFehler):
            domain.einreichen(eid, False)
        domain.senden(eid)
        self.assertEqual(len(domain.postausgang()), 1)

    def test_runde_2_pflichtfreigabe_alles_nur_mit_freigabe(self):
        fid, eid = self.fall_und_entwurf()
        setze_welle(2)
        with self.assertRaises(domain.FachFehler):
            domain.senden(eid)  # nicht eingereicht
        r = domain.einreichen(eid, False)
        self.assertEqual((r["stufe"], r["status"]), ("pflichtfreigabe", "zur_freigabe"))  # Fenster gibt es noch nicht
        with self.assertRaises(domain.FachFehler):
            domain.senden(eid)  # nicht freigegeben
        domain.freigeben(eid)
        domain.senden(eid)
        self.assertEqual(domain.postausgang()[0]["entwurf_id"], eid)
        with self.assertRaises(domain.FachFehler):
            domain.freigeben(eid)

    def test_ablehnen_braucht_grund_und_gibt_zurueck(self):
        fid, eid = self.fall_und_entwurf()
        setze_welle(2)
        domain.einreichen(eid, True)
        with self.assertRaises(domain.FachFehler):
            domain.ablehnen(eid, "  ")
        domain.ablehnen(eid, "Frist falsch")
        e = domain.entwuerfe(fid)[0]
        self.assertEqual((e["status"], e["ablehnung"]), ("entwurf", "Frist falsch"))
        domain.einreichen(eid, True)  # Claude überarbeitet und reicht erneut ein
        self.assertEqual(domain.entwuerfe(fid)[0]["status"], "zur_freigabe")

    def test_runde_3_eingriffsfenster_automatisch_genau_einmal(self):
        fid, eid = self.fall_und_entwurf()
        setze_welle(3)
        r = domain.einreichen(eid, False)
        self.assertEqual((r["stufe"], r["status"]), ("eingriffsfenster", "geplant"))
        self.assertGreater(r["sende_am"], domain.status()["jetzt"])
        with self.assertRaises(domain.FachFehler):
            domain.senden(eid)  # beschleunigen geht nicht
        self.assertEqual(domain.faellige_senden(), 0)
        res = domain.uhr_vorspulen(25)
        self.assertEqual(res["automatisch_gesendet"], 1)
        self.assertEqual(domain.uhr_vorspulen(1)["automatisch_gesendet"], 0)
        self.assertEqual(len(domain.postausgang()), 1)
        datei = outbox_dir() / domain.postausgang()[0]["datei"]
        self.assertIn("automatisch: ja", datei.read_text(encoding="utf-8"))
        auto = [e for e in domain.protokoll() if e["art"] == "gesendet"][0]
        self.assertEqual((auto["akteur"], auto["details"]["automatisch"]), ("system", True))

    def test_stoppen_haelt_die_mail_zurueck(self):
        fid, eid = self.fall_und_entwurf()
        setze_welle(3)
        domain.einreichen(eid, False)
        domain.stoppen(eid, akteur="claude")  # bremsen darf auch Claude
        self.assertEqual(domain.uhr_vorspulen(30)["automatisch_gesendet"], 0)
        self.assertEqual(domain.entwuerfe(fid)[0]["status"], "entwurf")
        with self.assertRaises(domain.FachFehler):
            domain.stoppen(eid)

    def test_key_account_bleibt_auch_im_fenster_bei_pflichtfreigabe(self):
        domain.welle_freischalten(1)
        domain.welle_freischalten(2, "hydrant")
        fid = domain.fall_anlegen("MSG-2-01", akteur="claude")["fall_id"]
        eid = domain.entwurf_anlegen(fid, "j.test@nordhafen.example.com", "Answer", "Hello", [], "claude")["entwurf_id"]
        setze_welle(3)
        r = domain.einreichen(eid, False)
        self.assertEqual(r["stufe"], "pflichtfreigabe")
        self.assertTrue(any("Key Account" in g for g in r["gruende"]))

    def test_uhr_nur_ab_runde_3_und_im_sinnvollen_bereich(self):
        domain.welle_freischalten(1)
        with self.assertRaises(domain.FachFehler):
            domain.uhr_vorspulen(1)
        setze_welle(3)
        for bad in (0, -1, 24 * 15, "x", None):
            with self.assertRaises(domain.FachFehler):
                domain.uhr_vorspulen(bad)
        t0 = domain.status()["jetzt"]
        domain.uhr_vorspulen(24)
        self.assertEqual(domain.status()["jetzt"][:10] > t0[:10], True)

    def test_einschaetzungen_und_bericht(self):
        domain.welle_freischalten(1)
        domain.einschaetzung_festhalten("K-1", "betroffen", "Produkt über Grenzwert", [{"typ": "artikel", "ref": "Art. 4 Abs. 3"}, {"typ": "produkt", "ref": "P-1"}], "2029-03-01", "claude")
        domain.einschaetzung_festhalten("K-1", "unklar", "Doch ein Messwert fehlt", [], None, "claude")  # überschreibt
        domain.einschaetzung_festhalten("K-2", "mittelbar", "Außerhalb, aber Lieferung in die EU", [], None, "claude")
        for args in (("K-9", "betroffen", "x"), ("K-1", "vielleicht", "x"), ("K-1", "betroffen", " ")):
            with self.assertRaises(domain.FachFehler):
                domain.einschaetzung_festhalten(args[0], args[1], args[2], [], None, "claude")
        self.assertEqual({e["kunde_id"]: e["ergebnis"] for e in domain.einschaetzungen()}, {"K-1": "unklar", "K-2": "mittelbar"})
        b = domain.bericht()
        self.assertEqual((b["einschaetzungen"]["unklar"], b["einschaetzungen"]["mittelbar"], b["einschaetzungen"]["ohne_einschaetzung"]), (1, 1, 0))

    def test_bericht_zaehlt_den_tag(self):
        fid, eid = self.fall_und_entwurf()
        setze_welle(2)
        domain.einreichen(eid, True)
        domain.freigeben(eid)
        domain.senden(eid)
        b = domain.bericht()
        self.assertEqual((b["versand"]["gesendet"], b["versand"]["mit_pflichtfreigabe"], b["kontrolle"]["freigegeben"]), (1, 1, 1))
        self.assertEqual(b["entwuerfe"]["von_claude"], 1)

    def test_belegpruefung_wird_beim_speichern_und_einreichen_aufgerufen(self):
        from sthamer_sys import belegpruefung
        alt = belegpruefung.pruefe_entwurf
        belegpruefung.pruefe_entwurf = lambda an, b, t, belege: ["Beleg fehlt."] if not belege else []
        try:
            domain.welle_freischalten(1)
            fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
            with self.assertRaises(domain.FachFehler) as cm:
                domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "B", "T", [], "claude")
            self.assertIn("Beleg fehlt", str(cm.exception))
            ok = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "B", "T", [{"typ": "produkt", "ref": "P-1"}], "claude")
            with self.assertRaises(domain.FachFehler):
                domain.entwurf_aendern(ok["entwurf_id"], {"belege": []}, "mensch")
        finally:
            belegpruefung.pruefe_entwurf = alt

    def test_abgewiesene_belegpruefung_steht_im_protokoll(self):
        from sthamer_sys import belegpruefung
        alt = belegpruefung.pruefe_entwurf
        belegpruefung.pruefe_entwurf = lambda an, b, t, belege: ["Das Datum ist keine Frist."] if "2031" in t else []
        try:
            domain.welle_freischalten(1)
            fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
            with self.assertRaises(domain.FachFehler):
                domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "B", "Ab 2031 gilt es.", [], "claude")
            ok = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "B", "Guten Tag", [], "claude")["entwurf_id"]
            with self.assertRaises(domain.FachFehler):
                domain.entwurf_aendern(ok, {"text": "Ab 2031 gilt es."}, "mensch")
        finally:
            belegpruefung.pruefe_entwurf = alt
        abg = [e for e in domain.protokoll() if e["art"] == "belegpruefung_abgewiesen"]
        self.assertEqual([(e["akteur"], e["fall_id"]) for e in abg], [("mensch", fid), ("claude", fid)])
        self.assertEqual(abg[0]["details"]["text"], "Das Datum ist keine Frist.")

    def test_speichern_ohne_aenderung_schreibt_nichts_ins_protokoll(self):
        fid, eid = FlussTest.fall_und_entwurf(self)
        vorher = len(domain.protokoll())
        r = domain.entwurf_aendern(eid, {"text": domain.entwuerfe(fid)[0]["text"]}, "mensch")
        self.assertTrue(r.get("unveraendert"))
        self.assertEqual(len(domain.protokoll()), vorher)

    def test_bericht_zaehlt_ruhende_kunden_nicht_als_fehlend(self):
        domain.welle_freischalten(1)
        for kid in ("K-1", "K-2"):
            domain.einschaetzung_festhalten(kid, "unklar", "Test", [], None, "claude")
        e = domain.bericht()["einschaetzungen"]
        self.assertEqual((e["aktive_kunden"], e["ohne_einschaetzung"]), (2, 0))

    def test_alter_lokaler_stand_wird_migriert(self):
        import sqlite3
        from sthamer_sys import store
        pfad = self.tmp / ".data" / "sthamer.db"
        pfad.parent.mkdir(parents=True, exist_ok=True)
        c = sqlite3.connect(str(pfad))
        c.execute("CREATE TABLE entwuerfe (id INTEGER PRIMARY KEY AUTOINCREMENT, fall_id INTEGER NOT NULL, an TEXT NOT NULL, betreff TEXT NOT NULL, "
                  "text TEXT NOT NULL, belege TEXT NOT NULL DEFAULT '[]', status TEXT NOT NULL DEFAULT 'entwurf', von TEXT NOT NULL, erstellt TEXT NOT NULL, geaendert TEXT NOT NULL)")
        c.commit()
        c.close()
        store._bereit.discard(str(pfad))
        with store.verbindung() as conn:
            spalten = {r["name"] for r in conn.execute("PRAGMA table_info(entwuerfe)").fetchall()}
        self.assertTrue({"stufe", "sende_am", "freigabe_von", "ablehnung"} <= spalten)


class McpPhase2Test(WeltTest):
    def call(self, name, args):
        r = mcp_server.aufrufen(name, args)
        return r, (r["content"][0]["text"] if r.get("isError") else __import__("json").loads(r["content"][0]["text"]))

    def test_claude_reicht_ein_kann_bremsen_aber_nicht_freigeben(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
        eid = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "A", "T", [], "claude")["entwurf_id"]
        r, _ = self.call("submit_draft", {"entwurf_id": eid, "rechtsaussage": False})
        self.assertTrue(r["isError"])  # noch Runde 1
        setze_welle(3)
        r, out = self.call("submit_draft", {"entwurf_id": eid, "rechtsaussage": False})
        self.assertEqual(out["status"], "geplant")
        _, q = self.call("list_queue", {})
        self.assertEqual(q[0]["id"], eid)
        r, _ = self.call("stop_scheduled_send", {"entwurf_id": eid})
        self.assertFalse(r.get("isError"))
        r, _ = self.call("submit_draft", {"entwurf_id": eid})  # rechtsaussage ist Pflicht
        self.assertTrue(r["isError"])
        r, _ = self.call("get_report_data", {})
        self.assertTrue(r["isError"])  # Runde 4 fehlt noch
        setze_welle(4)
        r, rep = self.call("get_report_data", {})
        self.assertIn("versand", rep)
        r, _ = self.call("record_assessment", {"kunde_id": "K-1", "ergebnis": "betroffen", "begruendung": "Test",
                                                "belege": [{"typ": "artikel", "ref": "Art. 4 Abs. 3"}, {"typ": "produkt", "ref": "P-1"}]})
        self.assertFalse(r.get("isError"))

    def test_claude_aendert_keine_eingereichten_entwuerfe(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
        eid = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "A", "T", [], "claude")["entwurf_id"]
        r, _ = self.call("update_draft", {"entwurf_id": eid, "text": "Neu"})
        self.assertFalse(r.get("isError"))  # noch Entwurf: ändern erlaubt
        setze_welle(2)
        self.call("submit_draft", {"entwurf_id": eid, "rechtsaussage": True})
        r, text = self.call("update_draft", {"entwurf_id": eid, "text": "Heimlich geändert"})
        self.assertTrue(r["isError"])
        self.assertIn("schon eingereicht", text)
        self.assertEqual(domain.entwuerfe(fid)[0]["text"], "Neu")
        domain.ablehnen(eid, "Bitte überarbeiten")  # der Mensch holt ihn zurück
        r, _ = self.call("update_draft", {"entwurf_id": eid, "text": "Überarbeitet"})
        self.assertFalse(r.get("isError"))


if __name__ == "__main__":
    unittest.main()
