import unittest

from botvar.stats import format, format_ranked, format_stats


SAMPLE_STATS = {
    "name": "Matthieu",
    "level": 50,
    "games": 1000,
    "wins": 400,
    "legends": [
        {"legend_name_key": "Jiro", "kos": 10, "games": 100, "wins": 50},
        {"legend_name_key": "Ada", "kos": 0, "games": 20, "wins": 5},
    ],
}

SAMPLE_RANKED = {
    "name": "Matthieu",
    "rating": 1000,
    "peak_rating": 1200,
    "tier": "Gold",
    "games": 200,
    "wins": 100,
    "legends": [
        {
            "legend_name_key": "Jiro",
            "rating": 1100,
            "peak_rating": 1300,
            "tier": "Gold",
            "games": 100,
            "wins": 50,
        },
        {
            "legend_name_key": "Ada",
            "rating": 900,
            "peak_rating": 950,
            "tier": "Silver",
            "games": 50,
            "wins": 20,
        },
    ],
}


class TestStats(unittest.TestCase):
    def test_format_stats(self):
        data = format_stats(SAMPLE_STATS)
        self.assertEqual(data["player"]["name"], "Matthieu")
        self.assertEqual(data["player"]["level"], 50)
        self.assertEqual(data["player"]["games"], {"total": 1000, "wins": 400})
        self.assertEqual([l["name"] for l in data["legends"]], ["Ada", "Jiro"])
        self.assertEqual(data["legends"][1]["kos"], 10)

    def test_format_ranked_sorted_by_peak(self):
        data = format_ranked(SAMPLE_RANKED)
        self.assertEqual(data["player"]["rating"]["peak"], 1200)
        self.assertEqual(data["legends"][0]["name"], "Jiro")
        self.assertEqual(data["legends"][1]["name"], "Ada")

    def test_format_dispatch(self):
        self.assertEqual(format(SAMPLE_STATS), format_stats(SAMPLE_STATS))
        self.assertEqual(format(SAMPLE_RANKED, "ranked"), format_ranked(SAMPLE_RANKED))


if __name__ == "__main__":
    unittest.main()
