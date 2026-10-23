# DPS970 – Activity 1

[![tests](../../actions/workflows/tests.yml/badge.svg)](../../actions/workflows/tests.yml)

| Folder | Question |
|---|---|
| [`spam_filter/`](spam_filter/) | Q1 – Spam filter email agent (simple reflex agent) |
| [`jug_search/`](jug_search/) | Q2 – Three-jug problem with breadth-first search |

Each folder's README has the written answers (parts a–c) and instructions for running that part.

## Running all tests

Python 3.9+, standard library only, nothing to install.

```bash
python -m unittest discover -s spam_filter -v
python -m unittest discover -s jug_search -v
```

GitHub Actions runs both on every push (`.github/workflows/tests.yml`).
