# Q2 – Three-Jug Search Problem

## Running

Requires Python 3.9+ (standard library only).

```bash
cd jug_search
python -m unittest -v     # run the tests
python search.py          # print the solution
```

Output:

```
start (0, 0, 0)
fill 12-gal jug                     -> (12, 0, 0)
pour 12-gal jug into 8-gal jug      -> (4, 8, 0)
pour 12-gal jug into 3-gal jug      -> (1, 8, 3)
```

The test data is a set of problem instances in `test_search.py`: the assignment's jugs, every goal amount from 0 to 12, a goal that is already true at the start, and two unsolvable instances (jugs of 6 and 4 gallons with a goal of 1, and a goal of 13).

## a) Problem formulation

- **States:** `(a, b, c)`, the gallons in the 12-, 8- and 3-gallon jugs, with `0 ≤ a ≤ 12`, `0 ≤ b ≤ 8`, `0 ≤ c ≤ 3`. That gives 13 × 9 × 4 = 468 possible states.
- **Initial state:** `(0, 0, 0)`.
- **Goal states:** any state where some jug holds exactly 1 gallon, e.g. `(1, 8, 3)` or `(0, 1, 0)`.
- **Actions** (only those that change the state are listed):
  - `Fill(i)`: fill jug *i* from the faucet (only if it isn't already full).
  - `Empty(i)`: pour jug *i* onto the ground (only if it isn't empty).
  - `Pour(i, j)`: pour jug *i* into jug *j* (only if *i* isn't empty and *j* isn't full).
- **Transition model:** `Result(s, a)`:
  - `Fill(i)`: jug *i* becomes its capacity.
  - `Empty(i)`: jug *i* becomes 0.
  - `Pour(i, j)`: move `m = min(s[i], cap[j] − s[j])`, so jug *i* becomes `s[i] − m` and jug *j* becomes `s[j] + m`. Pouring stops when the source is empty or the target is full.
- **Action cost:** 1 per action, so the path cost is the number of steps.

## b) Heuristic

A heuristic makes some sense but helps little. The state space has only 468 states, and blind search solves it instantly. Water totals also change in jumps (a fill or empty moves a whole jug's worth), so "distance" to the goal is hard to estimate.

An informal admissible heuristic:

- **h = 0** if some jug already holds 1 gallon.
- **h = 1** if a single pour leaves 1 gallon behind in the source jug. That is, for some pair of jugs, the source's amount minus the target's free space is exactly 1. For example, from `(4, 8, 0)`, pouring 4 gallons into the empty 3-gallon jug leaves 1.
- **h = 2** otherwise.

It never overestimates. Fill and empty can never produce 1 gallon (no jug holds exactly 1), so a state where no single pour reaches the goal needs at least two actions. So A* with this heuristic is still optimal. It only prunes a little, though.

## c) Is every search algorithm guaranteed to reach a goal?

No, not every algorithm. But every complete algorithm is, for this problem. The state space is finite (468 states), and a goal is reachable (fill 12, pour into 8, pour into 3), so:

- **Breadth-first, uniform-cost, iterative deepening, and A\*** are complete on finite spaces and will find the goal. Breadth-first and uniform-cost also find the shortest plan (3 steps) because every action costs 1.
- **Graph-search versions that track reached states** (including depth-first with a reached set) visit each state at most once, so they must hit the goal.
- **Tree-like depth-first search** (no cycle checking) is not guaranteed. It can loop forever, e.g. Fill(3) → Empty(3) → Fill(3)… The same goes for greedy best-first tree search.

Also, a goal has to exist for any algorithm to reach one. The test with jugs of 6 and 4 gallons and a goal of 1 shows breadth-first search correctly reporting failure: every amount is a multiple of gcd(6, 4) = 2.

## d) Implementation

`search.py` follows AIMA 4th edition:

- `JugProblem` has the AIMA problem interface: `initial`, `actions`, `result`, `is_goal`, `action_cost`.
- `Node`, `expand`, `path_actions` and `path_states` come from Section 3.3.
- `breadth_first_search` is Figure 3.9 line for line: an early goal test when a node is generated, a FIFO `frontier` (`collections.deque`), and a `reached` set. It returns `None` for failure.
