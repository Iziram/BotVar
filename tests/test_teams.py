import unittest

from botvar.teams import Team


class TestTeam(unittest.TestCase):
    def setUp(self):
        Team.init()

    def test_init_creates_teams(self):
        self.assertIsNotNone(Team.team_red)
        self.assertIsNotNone(Team.team_blue)
        self.assertIsNotNone(Team.team_waiter)
        self.assertEqual(len(Team.team_red), 0)

    def test_add_and_remove(self):
        Team.team_waiter.add("a")
        Team.team_waiter.add("b")
        self.assertEqual(len(Team.team_waiter), 2)
        Team.team_waiter.remove("a")
        self.assertEqual(Team.team_waiter.players, ["b"])

    def test_participants(self):
        Team.team_waiter.add("a")
        self.assertEqual(Team.participants(), ["a"])
        Team.init()
        self.assertEqual(Team.participants(), [])

    def test_select_splits_players(self):
        for i in range(6):
            Team.team_waiter.add(str(i))
        red, blue = Team.select()
        self.assertEqual(len(red), 3)
        self.assertEqual(len(blue), 3)
        self.assertEqual(sorted(red + blue), [str(i) for i in range(6)])

    def test_select_single_player(self):
        Team.team_waiter.add("solo")
        red, blue = Team.select()
        self.assertEqual(red + blue, ["solo"])


if __name__ == "__main__":
    unittest.main()
