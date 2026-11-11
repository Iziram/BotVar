"""Tests de :mod:`botvar.actions` (logique des commandes)."""
import unittest

import botvar.player as player_mod
from botvar import actions
from botvar.player import Player
from botvar.team import Team


class _ActionsTest(unittest.TestCase):
    """Base commune : réinitialise le registre des joueurs."""

    def setUp(self):
        Player.players = {}
        Player.legends = player_mod.LEGENDS.copy()


class TestLegend(_ActionsTest):
    def test_requires_prefix(self):
        self.assertEqual(actions.handle_command([], "1")["status"], "error")
        self.assertEqual(actions.handle_command(["x"], "1")["status"], "error")
        self.assertEqual(actions.handle_command(["!b"], "1")["status"], "error")

    def test_rdm(self):
        r = actions.handle_command(["!b", "legend", "rdm"], "1")
        self.assertEqual(r["status"], "success")
        self.assertIn("legend", r)
        self.assertNotIn(r["legend"], Player.get("1").legends)

    def test_list(self):
        r = actions.handle_command(["!b", "legend", "list"], "1")
        self.assertEqual(r["status"], "success")
        self.assertIn("legends", r)
        self.assertEqual(r["count"], len(Player.get("1").legends))

    def test_weapon(self):
        r = actions.handle_command(["!b", "legend", "weapon"], "1")
        self.assertEqual(r["status"], "success")
        self.assertIn(
            r["weapon"], ["principale", "secondaire", "aucune", "objets", "tous"]
        )

    def test_unknown_subcommand(self):
        self.assertEqual(
            actions.handle_command(["!b", "legend", "foo"], "1")["status"], "error"
        )


class TestPlayer(_ActionsTest):
    def test_steam_success(self):
        actions.api.get_brawlhalla_id_from_steam_id = lambda s: 12345
        r = actions.handle_command(["!b", "player", "steam", "765"], "1")
        self.assertEqual(r["status"], "success")
        self.assertTrue(Player.get("1").is_connected())

    def test_steam_failure(self):
        actions.api.get_brawlhalla_id_from_steam_id = lambda s: None
        r = actions.handle_command(["!b", "player", "steam", "765"], "1")
        self.assertEqual(r["status"], "error")

    def test_stats_error_when_disconnected(self):
        r = actions.handle_command(["!b", "player", "stats"], "1")
        self.assertEqual(r["status"], "error")
        self.assertIn("steam", r["message"].lower())

    def test_stats_success(self):
        p = Player("1")
        p.brawlhalla_id = 99
        actions.api.get_player_stats = lambda bid: {
            "name": "bob",
            "level": 1,
            "games": 2,
            "wins": 1,
            "legends": [],
        }
        r = actions.handle_command(["!b", "player", "stats"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["data"]["player"]["name"], "bob")
        self.assertEqual(r["filename"], "stats.json")

    def test_ranked_success(self):
        p = Player("1")
        p.brawlhalla_id = 99
        actions.api.get_player_ranked = lambda bid: {
            "name": "bob",
            "rating": 10,
            "peak_rating": 20,
            "tier": "x",
            "games": 3,
            "wins": 1,
            "legends": [],
        }
        r = actions.handle_command(["!b", "player", "ranked"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["filename"], "ranked.json")

    def test_clan_error_no_clan(self):
        p = Player("1")
        p.brawlhalla_id = 99
        actions.api.get_player_stats = lambda bid: {"name": "bob"}
        r = actions.handle_command(["!b", "player", "clan"], "1")
        self.assertEqual(r["status"], "error")
        self.assertIn("clan", r["message"].lower())

    def test_clan_success(self):
        p = Player("1")
        p.brawlhalla_id = 99
        actions.api.get_player_stats = lambda bid: {
            "name": "bob",
            "clan": {"clan_id": "c1"},
        }
        actions.api.get_clan = lambda cid: {"clan_id": "c1"}
        r = actions.handle_command(["!b", "player", "clan"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["data"], {"clan_id": "c1"})
        self.assertEqual(r["filename"], "clan.json")


class TestTeams(_ActionsTest):
    def setUp(self):
        super().setUp()
        Team.init()

    def test_new_with_and_without_code(self):
        r = actions.handle_command(["!b", "teams", "new"], "1")
        self.assertEqual(r["status"], "success")
        self.assertNotIn("RoomCode", r["text"])
        r = actions.handle_command(["!b", "teams", "new", "abc"], "1")
        self.assertIn("RoomCode : abc", r["text"])

    def test_list(self):
        r = actions.handle_command(["!b", "teams", "list"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(r["participants"], [])

    def test_select_and_reset(self):
        for i in range(4):
            Team.teamWaiter.add(i)
        r = actions.handle_command(["!b", "teams", "select"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(len(r["red"]) + len(r["blue"]), 4)
        r = actions.handle_command(["!b", "teams", "reset"], "1")
        self.assertEqual(r["status"], "success")
        self.assertEqual(len(Team.teamRed.players), 0)


class TestHelp(_ActionsTest):
    def test_general_and_topic(self):
        r = actions.handle_command(["!b", "help"], "1")
        self.assertEqual(r["status"], "success")
        self.assertIn("!b", r["text"])
        r = actions.handle_command(["!b", "help", "legend"], "1")
        self.assertIn("legend", r["text"])
        r = actions.handle_command(["!b", "help", "inconnue"], "1")
        self.assertEqual(r["status"], "error")

    def test_unknown_command(self):
        r = actions.handle_command(["!b", "nope"], "1")
        self.assertEqual(r["status"], "error")
        self.assertIn("n'existe pas", r["message"])


if __name__ == "__main__":
    unittest.main()
