"""Tests de :mod:`botvar.storage`."""
import os
import shutil
import tempfile
import unittest

from botvar import storage
from botvar.player import Player


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="botvar_test_")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_load_save_missing_returns_none(self):
        self.assertIsNone(storage.load_save(os.path.join(self.tmp, "nope.json")))

    def test_save_and_load_roundtrip(self):
        Player.players = {}
        path = os.path.join(self.tmp, "save.json")
        p = Player("42")
        p.steam_id = "765"
        p.brawlhalla_id = 99
        p.legends = ["Ada", "Brynn"]

        storage.save_players([p], path)
        data = storage.load_save(path)
        self.assertIsNotNone(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "42")
        self.assertEqual(data[0]["steam"], "765")
        self.assertEqual(data[0]["brawlhalla"], 99)
        self.assertEqual(data[0]["legends"], ["Ada", "Brynn"])

    def test_save_overwrites_existing(self):
        path = os.path.join(self.tmp, "save.json")
        storage.save_players([], path)
        storage.save_players([], path)
        self.assertEqual(storage.load_save(path), [])


if __name__ == "__main__":
    unittest.main()
