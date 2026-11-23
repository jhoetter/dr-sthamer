"""`start` ist der Ein-Befehl-Start: erst einrichten, dann die Kommandozentrale öffnen."""
import unittest
from unittest import mock

from sthamer_sys import cli


class StartTest(unittest.TestCase):
    def test_start_richtet_ein_und_startet_mit_browser(self):
        aufrufe = []
        with mock.patch.object(cli, "cmd_setup", side_effect=lambda a: aufrufe.append("setup") or 0), \
                mock.patch.object(cli, "cmd_serve", side_effect=lambda a: aufrufe.append(("serve", a.open)) or 0):
            self.assertEqual(cli.main(["start"]), 0)
        self.assertEqual(aufrufe, ["setup", ("serve", True)])

    def test_start_bricht_ab_wenn_einrichten_scheitert(self):
        with mock.patch.object(cli, "cmd_setup", return_value=1), \
                mock.patch.object(cli, "cmd_serve") as serve:
            self.assertEqual(cli.main(["start"]), 1)
        serve.assert_not_called()


if __name__ == "__main__":
    unittest.main()
