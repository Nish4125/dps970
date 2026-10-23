# DPS970 – Activity 2

[![tests](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)

| Folder | Question |
|---|---|
| [`connect_four/`](connect_four/) | Q1 – Connect Four move generator with Monte Carlo tree search: code, tests, experiments, and report |
| [`logic/`](logic/) | Q2–Q4 – Propositional logic: satisfiability, models, and resolution, with a truth-table checker |

## Running the tests

Python 3.8+, standard library only, nothing to install. From this folder:

```bash
python -m unittest discover -s connect_four -v   # Q1: 17 tests, about 2 seconds
python logic/truth_tables.py                     # Q2-Q4: prints the truth tables and asserts each answer
```

GitHub Actions runs both on every push (`.github/workflows/tests.yml` at the repo root).

## Other commands

```bash
cd connect_four
python connect4.py --seed 1                               # watch MCTS (X) play a random player (O)
python connect4.py --cycles 200 --expand 3 --height 2     # every MCTS setting can be changed from the command line
python experiments.py > results.md                        # regenerate the report's data (about 8 minutes)
```
