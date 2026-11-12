import unittest

from tests.helpers import WeltTest
from sthamer_sys import domain


class KernTest(WeltTest):
    def test_runde_1_ist_offen_runde_2_braucht_code(self):
        domain.welle_freischalten(1)
        self.assertEqual(len(domain.eingang()), 2)
        with self.assertRaises(domain.FachFehler):
            domain.welle_freischalten(2, "falsch")
        self.assertEqual(len(domain.eingang()), 2)
        domain.welle_freischalten(2, "  Hydrant ")
        self.assertEqual(len(domain.eingang()), 4)
        self.assertEqual(domain.aktuelle_welle(), 2)

    def test_abrufen_ist_idempotent(self):
        domain.welle_freischalten(1)
        self.assertEqual(domain.welle_freischalten(1)["neue_nachrichten"], 0)

    def test_fall_anlegen_einmal_mit_aufgabe(self):
        domain.welle_freischalten(1)
        a = domain.fall_anlegen("MSG-1-01")
        b = domain.fall_anlegen("MSG-1-01")
        self.assertTrue(a["neu"])
        self.assertFalse(b["neu"])
        f = domain.fall(a["fall_id"])
        self.assertEqual(len(f["aufgaben"]), 1)
        self.assertEqual(f["aufgaben"][0]["status"], "offen")

    def test_entwurf_nur_an_bekannte_kontakte(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02", akteur="claude")["fall_id"]
        with self.assertRaises(domain.FachFehler):
            domain.entwurf_anlegen(fid, "boese@evil.invalid", "Betreff", "Text", [], "claude")
        ok = domain.entwurf_anlegen(fid, "E.Muster@mueller.example.com", "Betreff", "Text", [], "claude")
        self.assertEqual(domain.entwuerfe(fid)[0]["an"], "e.muster@mueller.example.com")
        domain.entwurf_anlegen(fid, "ra@sthamer-uebung.example.com", "Intern", "Text", [], "claude")
        self.assertTrue(ok["entwurf_id"])

    def test_entwurf_eingaben_werden_geprueft(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
        for kwargs in ({"betreff": ""}, {"text": "x" * (domain.MAX_TEXT + 1)}, {"belege": [{"typ": "unsinn", "ref": "x"}]},
                       {"belege": "kein-array"}):
            args = dict(an="e.muster@mueller.example.com", betreff="B", text="T", belege=[])
            args.update(kwargs)
            with self.assertRaises(domain.FachFehler):
                domain.entwurf_anlegen(fid, args["an"], args["betreff"], args["text"], args["belege"], "claude")

    def test_senden_legt_datei_ab_und_nur_einmal(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
        eid = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "Antwort: Nachfüllen", "Guten Tag", [
            {"typ": "artikel", "ref": "Art. 4 Abs. 3"}], "claude")["entwurf_id"]
        r = domain.senden(eid)
        from sthamer_sys.paths import outbox_dir
        datei = outbox_dir() / r["datei"]
        self.assertTrue(datei.exists())
        inhalt = datei.read_text(encoding="utf-8")
        self.assertIn("Guten Tag", inhalt)
        self.assertNotIn("\r", inhalt)
        with self.assertRaises(domain.FachFehler):
            domain.senden(eid)
        self.assertEqual(len(domain.postausgang()), 1)
        with self.assertRaises(domain.FachFehler):
            domain.entwurf_aendern(eid, {"text": "zu spät"}, "mensch")

    def test_berichtigung_erscheint_erst_mit_ihrer_runde(self):
        self.assertEqual(domain.regelwerk_sichtbar()["verfuegbar"], [])
        domain.welle_freischalten(1)
        rw = domain.regelwerk_sichtbar()
        self.assertEqual(rw["verfuegbar"], ["vo-test.md"])
        self.assertNotIn("berichtigung", rw["regelwerk"])
        with self.assertRaises(domain.FachFehler):
            domain.verordnungstext("berichtigung-test.md")
        domain.welle_freischalten(2, "hydrant")
        rw = domain.regelwerk_sichtbar()
        self.assertIn("berichtigung-test.md", rw["verfuegbar"])
        self.assertEqual(rw["haupttext"], "vo-test.md")
        self.assertIn("berichtigung", rw["regelwerk"])
        self.assertIn("Art. 1", domain.verordnungstext()["text"])

    def test_protokoll_haelt_akteur_fest(self):
        domain.welle_freischalten(1)
        fid = domain.fall_anlegen("MSG-1-02", akteur="claude")["fall_id"]
        domain.notiz(fid, "Kunde bitte prüfen", "mensch")
        akteure = {e["akteur"] for e in domain.protokoll()}
        self.assertTrue({"claude", "mensch"} <= akteure)

    def test_stammdaten_umrechnung_und_leere_werte(self):
        self.assertEqual(domain.produkt_detail("P-2")["pfas_mg_l_umgerechnet"], 0.8)
        self.assertIsNone(domain.produkt_detail("P-3")["pfas_mg_l_umgerechnet"])
        self.assertEqual([p["id"] for p in domain.produkte_liste(nur_ohne_messwert=True)], ["P-3"])
        self.assertEqual(domain.kunde_detail("K-1")["lieferungen"][0]["produkt_name"], "Testschaum Ä")
        with self.assertRaises(domain.FachFehler):
            domain.kunde_detail("K-999")


if __name__ == "__main__":
    unittest.main()
