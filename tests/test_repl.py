import unittest

from botvar.player import Player
from botvar.repl import Repl
from botvar.teams import Team


class TestRepl(unittest.TestCase):
    def setUp(self):
        self.repl = Repl(user_id="test")

    def tearDown(self):
        Player.reset()
        Team.init()

    def test_help(self):
        self.assertIn("legend", self.repl._handle("help"))

    def test_quit(self):
        self.assertIn("Au revoir", self.repl._handle("quit"))

    def test_unknown_command(self):
        self.assertIn("inconnue", self.repl._handle("nope"))

    def test_legend_rdm(self):
        result = self.repl._handle("legend rdm")
        self.assertTrue(result.startswith("Utilise :"))

    def test_legend_weapon(self):
        self.assertIn("Arme(s) à utiliser :", self.repl._handle("legend weapon"))

    def test_legend_list(self):
        self.assertIn("Legends restantes", self.repl._handle("legend list"))

    def test_player_steam_requires_id(self):
        self.assertIn("Usage", self.repl._handle("player steam"))

    def test_player_stats_without_steam(self):
        self.assertIn("steam n'a pas été relié", self.repl._handle("player stats"))

    def test_teams_reset(self):
        self.assertIn("réinitialisée", self.repl._handle("teams reset"))

    def test_teams_new_with_roomcode(self):
        self.assertIn("RoomCode : 1234", self.repl._handle("teams new 1234"))

    def test_teams_list_empty(self):
        self.assertIn("Aucun participant", self.repl._handle("teams list"))

    def test_teams_list_and_select(self):
        Team.init()
        Team.team_waiter.add("a")
        Team.team_waiter.add("b")
        self.assertIn("a", self.repl._handle("teams list"))
        result = self.repl._handle("teams select")
        self.assertIn("Rouges", result)
        self.assertIn("Bleus", result)


if __name__ == "__main__":
    unittest.main()
