"""Eine Sitzung in einer Git-Nebenkopie (Worktree) darf keine zweite Kommandozentrale mit eigenem Stand starten."""
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sthamer_sys import cli, paths


def _git(*args, cwd):
    return subprocess.run(["git"] + list(args), cwd=str(cwd), capture_output=True, text=True)


@unittest.skipIf(shutil.which("git") is None, "Git fehlt")
class WorktreeErkennung(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="Sthamer Worktree Ü "))
        self.haupt = self.tmp / "dr-sthamer"
        self.haupt.mkdir()
        _git("init", "-q", cwd=self.haupt)
        _git("-c", "user.name=T", "-c", "user.email=t@example.invalid", "commit", "-q", "--allow-empty", "-m", "start", cwd=self.haupt)

    def tearDown(self):
        shutil.rmtree(str(self.tmp), ignore_errors=True)

    def test_hauptordner_ist_kein_worktree(self):
        self.assertIsNone(paths.worktree_hauptordner(self.haupt))

    def test_ohne_git_zip_betrieb_ist_kein_worktree(self):
        zip_ordner = self.tmp / "entpackt"
        zip_ordner.mkdir()
        self.assertIsNone(paths.worktree_hauptordner(zip_ordner))

    def test_worktree_der_app_wird_erkannt(self):
        wt = self.haupt / ".claude" / "worktrees" / "drill-1-abc123"
        r = _git("worktree", "add", "-q", "-b", "claude/drill-1-abc123", str(wt), cwd=self.haupt)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(paths.worktree_hauptordner(wt).resolve(), self.haupt.resolve())


class WorktreeStopp(unittest.TestCase):
    def test_einrichten_und_starten_halten_im_worktree_an(self):
        haupt = Path("/irgendwo/dr-sthamer")
        with mock.patch.object(paths, "worktree_hauptordner", return_value=haupt), \
                mock.patch.object(cli, "bereit_machen") as bereit, \
                mock.patch.object(cli, "hintergrund_starten") as hg, \
                mock.patch("sys.stderr") as err:
            self.assertEqual(cli.main(["setup"]), 3)
            self.assertEqual(cli.main(["start"]), 3)
            self.assertEqual(cli.main(["serve"]), 3)
        bereit.assert_not_called()
        hg.assert_not_called()
        gesagt = "".join(c.args[0] for c in err.write.call_args_list)
        self.assertIn("Nebenkopie", gesagt)
        self.assertIn(str(haupt), gesagt)

    def test_im_hauptordner_laeuft_alles_wie_bisher(self):
        with mock.patch.object(paths, "worktree_hauptordner", return_value=None):
            self.assertFalse(cli._worktree_stopp())


if __name__ == "__main__":
    unittest.main()
