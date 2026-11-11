import io
import unittest
from contextlib import redirect_stdout

from botvar.cli import build_parser, main


class TestCli(unittest.TestCase):
    def test_parser_version(self):
        parser = build_parser()
        with self.assertRaises(SystemExit):
            parser.parse_args(["--version"])

    def test_no_command_shows_help(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main([])
        self.assertEqual(rc, 0)
        self.assertIn("botvar", buf.getvalue().lower())

    def test_legend_rdm(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["legend", "rdm"])
        self.assertEqual(rc, 0)
        self.assertIn("Utilise :", buf.getvalue())

    def test_legend_weapon(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["legend", "weapon"])
        self.assertEqual(rc, 0)
        self.assertIn("Arme(s)", buf.getvalue())

    def test_player_stats_without_steam(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["player", "stats"])
        self.assertEqual(rc, 0)
        self.assertIn("steam", buf.getvalue())

    def test_player_steam_missing_id(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = main(["player", "steam"])
        self.assertEqual(rc, 2)

    def test_teams_commands(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(["teams", "reset"])
        self.assertIn("réinitialisée", buf.getvalue())
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(["teams", "new", "4321"])
        self.assertIn("RoomCode : 4321", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
