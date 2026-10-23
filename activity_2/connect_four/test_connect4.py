import random
import unittest

from connect4 import (WINDOWS, ConnectFour, evaluate, monte_carlo_tree_search, mcts_player, parse,
                      play_game, random_player, show)

g = ConnectFour()

# test data: positions with X to move (top row first)
WIN_IN_ONE = parse([".......",
                    ".......",
                    ".......",
                    "..X....",
                    "..XO...",
                    "..XOO.."])  # X wins with column 2
MUST_BLOCK = parse([".......",
                    ".......",
                    ".......",
                    ".......",
                    "..X....",
                    ".XXOOO."])  # O threatens column 6
TRAP = parse([".......",
              ".......",
              ".......",
              "X....O.",
              "OOO..X.",
              "OXX..X."])  # column 3 looks good but lets O win on top of it
FULL_DRAW = parse(["OXOXOXO",
                   "XOXOXOX",
                   "XOXOXOX",
                   "OXOXOXO",
                   "OXOXOXO",
                   "XOXOXOX"])


class TestGame(unittest.TestCase):
    def test_board_has_69_lines_of_four(self):
        self.assertEqual(len(WINDOWS), 69)  # 24 horizontal, 21 vertical, 12 + 12 diagonal

    def test_piece_drops_to_lowest_empty_row(self):
        s = g.result(g.result(g.initial, 3), 3)
        self.assertEqual(show(s).splitlines()[-3:-1], ["...O...", "...X..."])
        self.assertEqual(s.to_move, "X")

    def test_full_column_is_not_an_action(self):
        s = g.initial
        for _ in range(6):
            s = g.result(s, 0)
        self.assertEqual(g.actions(s), [1, 2, 3, 4, 5, 6])

    def test_wins_in_every_direction(self):
        for rows in (["......."] * 4 + ["OOO....", "XXXX..."],
                     ["......."] * 2 + ["X......", "XO.....", "XO.....", "XO....."],
                     ["......."] * 2 + ["...X...", "..XO...", ".XXO...", "XOOO..."],
                     ["......."] * 2 + ["X......", "OX.....", "XOX....", "OOOX..."]):
            s = parse(rows)
            self.assertEqual(s.utility, 1)
            self.assertTrue(g.is_terminal(s))
            self.assertEqual(g.utility(s, "O"), -1)

    def test_result_detects_the_winning_move(self):
        self.assertEqual(g.result(WIN_IN_ONE, 2).utility, 1)
        self.assertEqual(g.result(WIN_IN_ONE, 3).utility, 0)

    def test_full_board_is_a_draw(self):
        self.assertEqual(FULL_DRAW.utility, 0)
        self.assertTrue(g.is_terminal(FULL_DRAW))

    def test_parse_rejects_bad_boards(self):
        with self.assertRaises(ValueError):
            parse(["......."] * 5)
        with self.assertRaises(ValueError):
            parse(["......."] * 5 + ["XX....."])  # O can't be two pieces behind


class TestEvaluate(unittest.TestCase):
    def test_centre_opening_scores_highest(self):
        scores = [evaluate(g.result(g.initial, c).board, "X") for c in range(7)]
        self.assertEqual(max(range(7), key=scores.__getitem__), 3)
        self.assertEqual(scores[:3], scores[:3:-1])  # left-right symmetric

    def test_zero_sum_and_bounded(self):
        for c in range(7):
            b = g.result(MUST_BLOCK, c).board
            self.assertAlmostEqual(evaluate(b, "X"), -evaluate(b, "O"))
            self.assertLessEqual(abs(evaluate(b, "X")), 1)
        self.assertEqual(evaluate(g.result(WIN_IN_ONE, 2).board, "X"), 1)

    def test_objective_part_alone_falls_for_the_trap(self):
        best = max(g.actions(TRAP), key=lambda c: evaluate(g.result(TRAP, c).board, "X"))
        self.assertEqual(best, 3)


class TestMCTS(unittest.TestCase):
    def move(self, state, seed=0, **params):
        return monte_carlo_tree_search(state, g, rng=random.Random(seed), **params)

    def test_takes_the_win(self):
        for seed in range(3):
            self.assertEqual(self.move(WIN_IN_ONE, seed, cycles=200), 2)

    def test_blocks_the_threat(self):
        for seed in range(3):
            self.assertEqual(self.move(MUST_BLOCK, seed, cycles=500), 6)

    def test_avoids_the_trap(self):
        for seed in range(3):
            self.assertNotEqual(self.move(TRAP, seed, cycles=500), 3)

    def test_same_seed_gives_same_move(self):
        self.assertEqual(self.move(g.initial, 5, cycles=300), self.move(g.initial, 5, cycles=300))

    def test_expand_one_follows_the_objective_part(self):
        # with x = 1 only the heuristic's favourite child exists, so it must be chosen
        self.assertEqual(self.move(TRAP, cycles=50, expand=1), 3)

    def test_height_one_is_flat_monte_carlo(self):
        self.assertIn(self.move(MUST_BLOCK, cycles=700, height=1), g.actions(MUST_BLOCK))

    def test_beats_a_random_player(self):
        rng = random.Random(1)
        mcts = mcts_player(cycles=200, rng=rng)
        rand = lambda game, state: random_player(game, state, rng)
        for players, winner in (({"X": mcts, "O": rand}, 1), ({"X": rand, "O": mcts}, -1)):
            for _ in range(3):
                self.assertEqual(play_game(g, players).utility, winner)


if __name__ == "__main__":
    unittest.main()
