import unittest

from botvar import Player
from botvar.legends import LEGENDS


class TestPlayer(unittest.TestCase):
    def setUp(self):
        Player.reset()

    def tearDown(self):
        Player.reset()

    def test_player_registration(self):
        p = Player("123")
        self.assertIn("123", Player.players)
        self.assertIs(Player.get("123"), p)

    def test_player_not_connected_by_default(self):
        p = Player("123")
        self.assertFalse(p.is_connected())

    def test_fournish_without_connection_uses_static_list(self):
        p = Player("123")
        p.fournish()
        self.assertEqual(sorted(p.legends), sorted(LEGENDS))

    def test_random_returns_a_legend_and_removes_it(self):
        p = Player("123")
        p.fournish()
        initial = len(p.legends)
        drawn = p.random()
        self.assertNotIn(drawn, p.legends)
        self.assertEqual(len(p.legends), initial - 1)

    def test_random_refills_empty_list(self):
        p = Player("123")
        p.legends = []
        drawn = p.random()
        self.assertIn(drawn, LEGENDS)
        self.assertEqual(len(p.legends), len(LEGENDS) - 1)

    def test_rest_formats_two_columns(self):
        p = Player("123")
        p.legends = ["Ada", "Jiro", "Kor"]
        text = p.rest()
        self.assertIn("Ada", text)
        self.assertIn("Jiro", text)
        self.assertIn("Kor", text)
        self.assertNotIn("_", text)

    def test_to_json_roundtrip(self):
        p = Player("456")
        p.steam_id = "76561198320268538"
        p.brawlhalla_id = 8711008
        p.legends = ["Jiro"]
        data = p.to_json()
        self.assertEqual(data["name"], "456")
        self.assertEqual(data["steam"], "76561198320268538")
        self.assertEqual(data["brawlhalla"], 8711008)
        self.assertEqual(data["legends"], ["Jiro"])
        Player.players = {}
        restored = Player.from_json(data)
        self.assertEqual(restored.steam_id, p.steam_id)
        self.assertEqual(restored.brawlhalla_id, p.brawlhalla_id)
        self.assertEqual(restored.legends, p.legends)

    def test_load_from_save(self):
        import json
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "save.json"
            path.write_text(
                json.dumps(
                    [
                        {
                            "name": "789",
                            "steam": "123",
                            "brawlhalla": 456,
                            "legends": ["Ada"],
                        }
                    ]
                )
            )
            Player.load_from_save(str(path))
            self.assertIn("789", Player.players)
            self.assertEqual(Player.get("789").brawlhalla_id, 456)

    def test_load_from_save_missing_file(self):
        Player.load_from_save("/nonexistent/save.json")
        self.assertEqual(Player.players, {})

    def test_weapon_returns_known_value(self):
        self.assertIn(Player.weapon(), ["principale", "secondaire", "aucune", "objets", "tous"])

    def test_old_api_aliases(self):
        p = Player("42")
        self.assertEqual(p.toJson(), p.to_json())
        self.assertEqual(p.isConnected(), p.is_connected())


if __name__ == "__main__":
    unittest.main()
