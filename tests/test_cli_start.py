"""`start` ist der Ein-Befehl-Start: erst einrichten, dann die Kommandozentrale im Hintergrund starten und sofort zurückkehren."""
import os
import unittest
from unittest import mock

from sthamer_sys import cli


class StartTest(unittest.TestCase):
    def test_start_richtet_ein_und_startet_im_hintergrund(self):
        aufrufe = []
        with mock.patch.object(cli, "cmd_setup", side_effect=lambda a: aufrufe.append("setup") or 0), \
                mock.patch.object(cli, "hintergrund_starten", side_effect=lambda port, browser=True: aufrufe.append(("hintergrund", port, browser)) or 0), \
                mock.patch.object(cli, "cmd_serve") as serve:
            self.assertEqual(cli.main(["start"]), 0)
        self.assertEqual(aufrufe, ["setup", ("hintergrund", cli.DEFAULT_PORT, True)])
        serve.assert_not_called()  # kein Befehl, der nie endet

    def test_start_mit_vordergrund_bleibt_stehen_wie_serve(self):
        aufrufe = []
        with mock.patch.object(cli, "cmd_setup", side_effect=lambda a: aufrufe.append("setup") or 0), \
                mock.patch.object(cli, "cmd_serve", side_effect=lambda a: aufrufe.append(("serve", a.open)) or 0), \
                mock.patch.object(cli, "hintergrund_starten") as hg:
            self.assertEqual(cli.main(["start", "--vordergrund"]), 0)
        self.assertEqual(aufrufe, ["setup", ("serve", True)])
        hg.assert_not_called()

    def test_start_bricht_ab_wenn_einrichten_scheitert(self):
        with mock.patch.object(cli, "cmd_setup", return_value=1), \
                mock.patch.object(cli, "hintergrund_starten") as hg:
            self.assertEqual(cli.main(["start"]), 1)
        hg.assert_not_called()


class HintergrundTest(unittest.TestCase):
    def test_laeuft_sie_schon_wird_nur_geoeffnet(self):
        with mock.patch.object(cli, "_server_info", return_value=(3005, "http://127.0.0.1:3005")), \
                mock.patch.object(cli.subprocess, "Popen") as popen, \
                mock.patch("webbrowser.open") as browser:
            self.assertEqual(cli.hintergrund_starten(3005), 0)
        popen.assert_not_called()
        browser.assert_called_once_with("http://127.0.0.1:3005")

    def test_startet_losgeloest_und_kehrt_zurueck_sobald_sie_antwortet(self):
        antworten = iter([None, None, (3005, "http://127.0.0.1:3005")])  # nicht da, nicht da, jetzt da
        with mock.patch.object(cli, "_server_info", side_effect=lambda p: next(antworten)), \
                mock.patch.object(cli.subprocess, "Popen") as popen, \
                mock.patch("time.sleep"):
            self.assertEqual(cli.hintergrund_starten(3005), 0)
        popen.assert_called_once()
        befehl = popen.call_args[0][0]
        self.assertEqual(befehl[2:], ["serve", "--port", "3005", "--open"])
        optionen = popen.call_args[1]
        if os.name == "nt":
            self.assertTrue(optionen["creationflags"] & 0x00000008)  # DETACHED_PROCESS
        else:
            self.assertTrue(optionen["start_new_session"])  # überlebt das Ende des Befehls
        self.assertEqual(optionen["stdin"], cli.subprocess.DEVNULL)

    def test_antwortet_sie_nie_endet_der_befehl_mit_fehler(self):
        with mock.patch.object(cli, "_server_info", return_value=None), \
                mock.patch.object(cli.subprocess, "Popen"), \
                mock.patch("time.sleep"), \
                mock.patch("time.time", side_effect=[0, 1, 2, 100, 100]):
            self.assertEqual(cli.hintergrund_starten(3005, warten=3), 1)

    def test_kein_browser_oeffnet_nichts(self):
        with mock.patch.object(cli, "_server_info", return_value=(3005, "http://127.0.0.1:3005")), \
                mock.patch("webbrowser.open") as browser:
            self.assertEqual(cli.hintergrund_starten(3005, browser=False), 0)
        browser.assert_not_called()
        antworten = iter([None, (3005, "http://127.0.0.1:3005")])
        with mock.patch.object(cli, "_server_info", side_effect=lambda p: next(antworten)), \
                mock.patch.object(cli.subprocess, "Popen") as popen, mock.patch("time.sleep"):
            self.assertEqual(cli.hintergrund_starten(3005, browser=False), 0)
        self.assertNotIn("--open", popen.call_args[0][0])

    def test_start_kein_browser_reicht_es_durch(self):
        with mock.patch.object(cli, "cmd_setup", return_value=0), \
                mock.patch.object(cli, "hintergrund_starten", return_value=0) as hg:
            self.assertEqual(cli.main(["start", "--kein-browser"]), 0)
        hg.assert_called_once_with(cli.DEFAULT_PORT, browser=False)


if __name__ == "__main__":
    unittest.main()
