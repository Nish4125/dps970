"""Runs the experiments in the report and prints the tables as markdown.

    python experiments.py > results.md           # 20 seeds per setting, 40 games per match, ~8 minutes
    python experiments.py --runs 5 --games 10    # quicker
"""
import argparse
import random
import time
from collections import Counter

from connect4 import ConnectFour, mcts_player, monte_carlo_tree_search, parse, play_game, random_player

g = ConnectFour()
BASE = dict(cycles=1000, expand=7, height=4, C=1.4, w=1.0)

# (name, position with X to move, test for a good move or None if there is no single right answer)
POSITIONS = [
    ("Opening: centre %", g.initial, lambda m: m == 3),
    ("Must block: col 6 %", parse([".......",
                                   ".......",
                                   ".......",
                                   ".......",
                                   "..X....",
                                   ".XXOOO."]), lambda m: m == 6),
    ("Trap: avoids col 3 %", parse([".......",
                                    ".......",
                                    ".......",
                                    "X....O.",
                                    "OOO..X.",
                                    "OXX..X."]), lambda m: m != 3),
    ("Quiet midgame: moves chosen", parse([".......",
                                           ".......",
                                           ".......",
                                           "...O...",
                                           ".O.XO.O",
                                           ".X.XOXX"]), None),
]

SWEEPS = [
    ("Utility function (C = exploration weight, w = objective weight)", ["C", "w"],
     [(1.4, 0), (1.4, 0.5), (1.4, 1), (1.4, 3), (1.4, 10), (0, 1), (0.5, 1), (3, 1)]),
    ("Utility function with only 100 cycles", ["cycles", "w"], [(100, 0), (100, 1), (100, 3), (100, 10)]),
    ("Number of cycles", ["cycles"], [(n,) for n in (25, 50, 100, 250, 500, 1000, 2500, 5000)]),
    ("Expansion nodes x", ["expand"], [(x,) for x in (1, 2, 3, 4, 5, 7)]),
    ("Tree height", ["height"], [(h,) for h in (1, 2, 3, 4, 6, 10, 42)]),
]

MATCHES = [  # (label, changes for player A, changes for player B), both start from BASE with 300 cycles
    ("w = 1 vs w = 0", dict(w=1), dict(w=0)),
    ("height 4 vs height 1", dict(height=4), dict(height=1)),
    ("height 4 vs height 42", dict(height=4), dict(height=42)),
    ("x = 3 vs x = 7", dict(expand=3), dict(expand=7)),
    ("1000 cycles vs 300 cycles", dict(cycles=1000), dict()),
]


def sweep(title, keys, values, runs):
    head = " | ".join(name for name, _, _ in POSITIONS)
    print(f"### {title}\n\n| {', '.join(keys)} | {head} | ms/move |\n|" + "---|" * (len(POSITIONS) + 2))
    for value in values:
        params = {**BASE, **dict(zip(keys, value))}
        cells, start = [], time.perf_counter()
        for _, state, good in POSITIONS:
            moves = [monte_carlo_tree_search(state, g, rng=random.Random(seed), **params) for seed in range(runs)]
            if good:
                cells.append(f"{100 * sum(map(good, moves)) // runs}")
            else:
                cells.append(" ".join(f"{m}:{n}" for m, n in Counter(moves).most_common()))
        ms = 1000 * (time.perf_counter() - start) / (runs * len(POSITIONS))
        print(f"| {', '.join(map(str, value))} | {' | '.join(cells)} | {ms:.0f} |")
    print()


def match(label, a, b, games):
    """A and B swap colours every game. Returns A's wins, draws, losses."""
    score = Counter()
    for i in range(games):
        rng = random.Random(i)
        pa = mcts_player(rng=rng, **{**BASE, "cycles": 300, **a})
        pb = mcts_player(rng=rng, **{**BASE, "cycles": 300, **b})
        players, a_is = ({"X": pa, "O": pb}, 1) if i % 2 == 0 else ({"X": pb, "O": pa}, -1)
        u = play_game(g, players).utility * a_is
        score["win" if u > 0 else "loss" if u < 0 else "draw"] += 1
    print(f"| {label} | {score['win']} | {score['draw']} | {score['loss']} |")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=20, help="seeds per setting")
    ap.add_argument("--games", type=int, default=40, help="games per head-to-head match")
    args = ap.parse_args()
    print(f"Base settings: {BASE}. Each cell uses seeds 0..{args.runs - 1}; one setting is changed per row.\n")
    for title, keys, values in SWEEPS:
        sweep(title, keys, values, args.runs)

    print(f"### Head-to-head ({args.games} games, colours alternate, 300 cycles unless stated)\n")
    print("| Match (A vs B) | A wins | draws | B wins |\n|---|---|---|---|")
    for label, a, b in MATCHES:
        match(label, a, b, args.games)
    rng = random.Random(0)
    wins = sum(play_game(g, {"X": mcts_player(rng=rng, **{**BASE, "cycles": 100}),
                             "O": lambda game, s: random_player(game, s, rng)}).utility == 1 for _ in range(args.games))
    print(f"| 100-cycle MCTS (X) vs random player | {wins} | - | {args.games - wins} |")
