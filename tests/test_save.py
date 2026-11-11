import json
import tempfile
import unittest
from pathlib import Path

from botvar.player import Player
from botvar.save import load, save


class TestSave(unittest.TestCase):
    def setUp(self):
        Player.reset()

    def tearDown(self):
        Player.reset()

    def test_save_and_load(self):
        p = Player("111")
        p.steam_id = "abc"
        p.brawlhalla_id = 999
        p.legends = ["Ada"]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "save.json"
            save(Player.players, path)
            self.assertTrue(path.exists())
            data = json.loads(path.read_text())
            self.assertEqual(data[0]["name"], "111")
            self.assertEqual(data[0]["brawlhalla"], 999)
            loaded = load(path)
            self.assertEqual(loaded, data)

    def test_load_missing_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(load(Path(d) / "nope.json"), [])


if __name__ == "__main__":
    unittest.main()
