"""Tests de :mod:`botvar.team`."""
import unittest

from botvar.team import Team


class TestTeam(unittest.TestCase):
    def setUp(self):
        Team.init()

    def test_init_creates_three_teams(self):
        self.assertEqual(Team.teamRed.color, "red")
        self.assertEqual(Team.teamBlue.color, "blue")
        self.assertEqual(Team.teamWaiter.color, "waiter")
        self.assertEqual(len(Team.teamRed), 0)

    def test_add_and_remove(self):
        Team.teamRed.add("a")
        Team.teamRed.add("b")
        self.assertEqual(len(Team.teamRed), 2)
        Team.teamRed.remove("a")
        self.assertEqual(len(Team.teamRed), 1)
        Team.teamRed.remove("a")  # double removal is a no-op
        self.assertEqual(len(Team.teamRed), 1)

    def test_participants_empty(self):
        self.assertEqual(Team.participants(), [])

    def test_participants_from_waiter(self):
        Team.teamWaiter.add("x")
        self.assertEqual(Team.participants(), ["x"])

    def test_selection_splits_evenly(self):
        for i in range(6):
            Team.teamWaiter.add(i)
        Team.selection()
        self.assertEqual(len(Team.teamRed.players) + len(Team.teamBlue.players), 6)
        self.assertEqual(len(Team.teamRed.players), 3)
        self.assertEqual(len(Team.teamBlue.players), 3)

    def test_selection_handles_odd(self):
        for i in range(5):
            Team.teamWaiter.add(i)
        Team.selection()
        self.assertEqual(len(Team.teamRed.players) + len(Team.teamBlue.players), 5)
        self.assertLessEqual(
            abs(len(Team.teamRed.players) - len(Team.teamBlue.players)), 1
        )


if __name__ == "__main__":
    unittest.main()
