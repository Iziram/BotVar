"""Tests de :mod:`botvar.render` et de :mod:`botvar.cli`."""
import io
import json
import os
import shutil
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import botvar.player as player_mod
from botvar import cli, render
from botvar.player import Player


class TestRender(unittest.TestCase):
    def test_error(self):
        out = render.render({"status": "error", "message": "boom"})
        self.assertIn("[erreur]", out)
        self.assertIn("boom", out)

    def test_legend(self):
        out = render.render({"status": "success", "legend": "Ada"})
        self.assertIn("Utilise : Ada", out)

    def test_weapon(self):
        out = render.render({"status": "success", "weapon": "objets"})
        self.assertIn("objets", out)

    def test_data_json(self):
        out = render.render(
            {"status": "success", "data": {"a": 1}, "filename": "x.json"}
        )
        self.assertEqual(json.loads(out), {"a": 1})

    def test_participants(self):
        out = render.render({"status": "success", "participants": [1, 2]})
        self.assertIn("- 1", out)
        self.assertIn("- 2", out)

    def test_save_json(self):
        tmp = tempfile.mkdtemp(prefix="botvar_render_")
        self.addCleanup(shutil.rmtree, tmp, True)
        old = os.getcwd()
        os.chdir(tmp)
        self.addCleanup(os.chdir, old)
        path = render.save_json(
            {"status": "success", "data": {"a": 1}, "filename": "out.json"}
        )
        self.assertEqual(path, "out.json")
        with open("out.json") as f:
            self.assertEqual(json.load(f), {"a": 1})

    def test_save_json_no_data(self):
        self.assertIsNone(render.save_json({"status": "success"}))


class TestCli(unittest.TestCase):
    def _run(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = cli.main(argv)
        return rc, out.getvalue(), err.getvalue()

    def _reset(self):
        Player.players = {}
        Player.legends = player_mod.LEGENDS.copy()

    def test_legend_rdm(self):
        self._reset()
        rc, out, _ = self._run(["legend", "rdm", "--player", "9"])
        self.assertEqual(rc, 0)
        self.assertIn("Utilise :", out)

    def test_help(self):
        rc, out, _ = self._run(["help"])
        self.assertEqual(rc, 0)
        self.assertIn("!b", out)

    def test_player_steam_no_id(self):
        rc, _, err = self._run(["player", "steam"])
        self.assertEqual(rc, 1)
        self.assertIn("requi", err)

    def test_player_stats_disconnected(self):
        self._reset()
        rc, out, _ = self._run(["player", "stats", "--player", "1"])
        self.assertEqual(rc, 1)
        self.assertIn("[erreur]", out)


if __name__ == "__main__":
    unittest.main()
