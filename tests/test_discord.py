import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from botvar.discord_bot import load_tokens, make_bot


class TestDiscord(unittest.TestCase):
    def test_load_tokens_from_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "apikey.txt"
            path.write_text("fakekey faketoken\n")
            with patch.dict(
                os.environ, {"BRAWLHALLA_API_KEY": "", "DISCORD_TOKEN": ""}, clear=False
            ):
                api_key, token = load_tokens(str(path))
        self.assertEqual(api_key, "fakekey")
        self.assertEqual(token, "faketoken")

    def test_load_tokens_from_env(self):
        with patch.dict(
            os.environ,
            {"BRAWLHALLA_API_KEY": "envkey", "DISCORD_TOKEN": "envtoken"},
            clear=False,
        ):
            api_key, token = load_tokens("/nonexistent/apikey.txt")
        self.assertEqual(api_key, "envkey")
        self.assertEqual(token, "envtoken")

    def test_make_bot_returns_client(self):
        import discord

        client = make_bot()
        self.assertIsInstance(client, discord.Client)


if __name__ == "__main__":
    unittest.main()
