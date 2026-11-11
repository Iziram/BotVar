"""Tests de :mod:`botvar.player`."""
import unittest

import botvar.player as player_mod
from botvar.player import Player, statistics_formatter


def _reset_players():
    Player.players = {}
    Player.legends = player_mod.LEGENDS.copy()


class TestPlayer(unittest.TestCase):
    def setUp(self):
        _reset_players()

    def test_creation_and_registry(self):
        p = Player("123")
        self.assertEqual(p.name, "123")
        self.assertIsNone(p.steam_id)
        self.assertIsNone(p.brawlhalla_id)
        self.assertIs(Player.get("123"), p)
        p2 = Player("123")
        self.assertIs(Player.players["123"], p)
        _ = p2

    def test_not_connected_by_default(self):
        self.assertFalse(Player("123").is_connected())

    def test_connected_when_brawlhalla_set(self):
        p = Player("123")
        p.brawlhalla_id = 42
        self.assertTrue(p.is_connected())

    def test_furnish_uses_static_when_disconnected(self):
        p = Player("123")
        p.furnish()
        self.assertEqual(p.legends, Player.legends)

    def test_random_pops_a_legend(self):
        p = Player("123")
        p.legends = ["A", "B", "C"]
        before = len(p.legends)
        drawn = p.random()
        self.assertIn(drawn, ["A", "B", "C"])
        self.assertNotIn(drawn, p.legends)
        self.assertEqual(len(p.legends), before - 1)

    def test_random_refills_when_empty(self):
        p = Player("123")
        p.legends = []
        drawn = p.random()
        self.assertIn(drawn, player_mod.LEGENDS)

    def test_rest_formats_two_columns(self):
        p = Player("123")
        p.legends = ["Ada", "Brynn", "Cassidy", "Diana"]
        out = p.rest()
        self.assertIn("Ada", out)
        self.assertIn("Diana", out)
        p.legends = ["Lord_Vraxx"]
        self.assertIn("Lord Vraxx", p.rest())

    def test_to_json_and_from_json_roundtrip(self):
        p = Player("123")
        p.steam_id = "765"
        p.brawlhalla_id = 88
        p.legends = ["Ada"]
        data = p.to_json()
        _reset_players()
        q = Player.from_json(data)
        self.assertEqual(q.name, "123")
        self.assertEqual(q.steam_id, "765")
        self.assertEqual(q.brawlhalla_id, 88)
        self.assertEqual(q.legends, ["Ada"])

    def test_load_from_save_missing_file(self):
        import tempfile
        import os

        path = os.path.join(tempfile.mkdtemp(), "nope.json")
        Player.load_from_save(path)
        self.assertEqual(Player.players, {})

    def test_load_from_save_existing(self):
        import json
        import tempfile
        import os

        path = os.path.join(tempfile.mkdtemp(), "save.json")
        with open(path, "w") as f:
            json.dump(
                [{"name": "1", "steam": "s1", "brawlhalla": 11, "legends": ["Ada"]}]
            , f)
        Player.load_from_save(path)
        self.assertIn("1", Player.players)
        self.assertEqual(Player.players["1"].brawlhalla_id, 11)


class TestStatisticsFormatter(unittest.TestCase):
    def test_stat(self):
        stats = {
            "name": "bob",
            "level": 30,
            "games": 100,
            "wins": 40,
            "legends": [
                {"legend_name_key": "B", "kos": 5, "games": 10, "wins": 3},
                {"legend_name_key": "A", "kos": 2, "games": 8, "wins": 1},
            ],
        }
        out = statistics_formatter(stats)
        self.assertEqual(out["player"]["name"], "bob")
        self.assertEqual(out["player"]["games"], {"total": 100, "wins": 40})
        self.assertEqual([l["name"] for l in out["legends"]], ["A", "B"])

    def test_ranked(self):
        stats = {
            "name": "bob",
            "rating": 1200,
            "peak_rating": 1500,
            "tier": "gold",
            "games": 50,
            "wins": 20,
            "legends": [
                {"legend_name_key": "A", "rating": 100, "peak_rating": 200, "tier": "x",
                 "games": 5, "wins": 2},
                {"legend_name_key": "B", "rating": 300, "peak_rating": 500, "tier": "y",
                 "games": 7, "wins": 4},
            ],
        }
        out = statistics_formatter(stats, "ranked")
        self.assertEqual(out["player"]["rating"]["peak"], 1500)
        self.assertEqual([l["name"] for l in out["legends"]], ["B", "A"])


class TestWeapon(unittest.TestCase):
    def test_returns_known_value(self):
        self.assertIn(
            Player.weapon(),
            ["principale", "secondaire", "aucune", "objets", "tous"],
        )


if __name__ == "__main__":
    unittest.main()
