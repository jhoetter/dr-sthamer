"""`reset` leert den lokalen Stand, auch wenn die Datenbankdatei gerade von der Kommandozentrale benutzt wird."""
import unittest

from sthamer_sys import cli, domain
from sthamer_sys.paths import outbox_dir
from tests.helpers import WeltTest


class ResetTest(WeltTest):
    def test_reset_leert_alles_und_ruft_runde_1_neu_ab(self):
        domain.welle_freischalten(1)
        domain.welle_freischalten(2, "testcode")
        fid = domain.fall_anlegen("MSG-1-02")["fall_id"]
        eid = domain.entwurf_anlegen(fid, "e.muster@mueller.example.com", "A", "Guten Tag", [], "claude")["entwurf_id"]
        domain.einreichen(eid, True)
        domain.freigeben(eid)
        domain.senden(eid)
        self.assertEqual(len(list(outbox_dir().glob("*.md"))), 1)
        self.assertEqual(cli.main(["reset"]), 1)  # ohne --yes passiert nichts
        self.assertEqual(domain.status()["faelle"], 1)
        self.assertEqual(cli.main(["reset", "--yes"]), 0)
        s = domain.status()
        self.assertEqual((s["faelle"], s["gesendet"], s["welle"], s["nachrichten"]), (0, 0, 1, 2))
        self.assertEqual(list(outbox_dir().glob("*.md")), [])
        # Fall-Nummern beginnen wieder bei 1
        self.assertEqual(domain.fall_anlegen("MSG-1-02")["fall_id"], 1)


if __name__ == "__main__":
    unittest.main()
