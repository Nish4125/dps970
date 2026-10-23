# Q1 – Connect Four Move Generator with Monte Carlo Tree Search

## Running

Python 3.8+, standard library only.

```bash
cd connect_four
python -m unittest -v                  # 17 tests, about 2 seconds
python connect4.py --seed 1            # MCTS (X) plays a random player (O), printing the board after each move
python connect4.py --cycles 200 --expand 3 --height 2 --C 1.4 --w 1 --seed 7
python experiments.py > results.md     # regenerates every table in this report (about 8 minutes)
```

| File | Contents |
|---|---|
| `connect4.py` | The game (AIMA `Game` interface), the objective evaluation, and MCTS (Figure 5.11) |
| `test_connect4.py` | Tests and test data (win-in-one, must-block, trap, and full-board draw positions) |
| `experiments.py` | The experiment runner; its raw output is in `results.md` |

## Design

The code follows the AIMA 4th edition snippets: the `Game` interface from Chapter 5 (`to_move`, `actions`, `result`, `is_terminal`, `utility`), plus `MCT_Node`, `ucb`, `monte_carlo_tree_search` and `play_game` from the book's code (`games4e.py`). The main loop is Figure 5.11 line for line:

```python
root = MCT_Node(state=state)
for _ in range(cycles):                        # while IS-TIME-REMAINING()
    leaf = select(root)                        # leaf <- SELECT(tree)
    child = expand_leaf(leaf)                  # child <- EXPAND(leaf)
    back_propagate(simulate(child.state), child)
return root.children[max(root.children, key=lambda c: c.N)]   # move with the most playouts
```

**Board.** A state is `(board, to_move, utility)`. The board is a tuple of 42 cells, and `utility` is +1 or −1 once someone has won. `result` drops the piece into the lowest empty row and checks for a win only through the cell just played.

**Selection.** Starting at the root, select repeatedly moves to the child with the highest selection utility:

\[ \text{UCB}(n) = \underbrace{\frac{U(n)}{N(n)} + C\sqrt{\frac{\ln N(\text{parent}(n))}{N(n)}}}_{\text{playout part (UCB1)}} \;+\; \underbrace{w\,\frac{h(n)}{N(n)+1}}_{\text{objective part}} \]

- **Playout part.** \(U(n)\) is the total playout result for the player who moved into node \(n\) (win 1, draw ½, loss 0), and \(N(n)\) is the number of playouts through \(n\). This is the UCB1 formula from Section 5.4, with exploration constant \(C\).
- **Objective part.** \(h(n) \in [-1, 1]\) is `evaluate(board, player)`, computed from the rules of the game alone. It looks at all 69 lines of four on the board. Each line still open to only one side scores 1, 4 or 16 for that side, depending on whether it holds 1, 2 or 3 of that side's pieces. Lines open to the opponent count negatively, a completed four scores ±1, and the total is squashed with `tanh`. Centre cells sit on more lines (13 for a centre cell, 3 for a corner), so centre control comes out of the count without a special rule.
- The objective part is divided by \(N+1\) (known in the literature as *progressive bias*). It guides the search while a node has few playouts, then fades so the real playout statistics take over. \(w\) sets how strongly the objective part counts, and \(w = 0\) gives plain UCB1.
- Unvisited children score ∞, as in AIMA, so each child is tried once before UCB comparisons begin.

**Expansion: x nodes per level.** When a leaf is expanded, all legal moves are scored with the objective function, and only the best `expand` (= x) become children. Ties are broken randomly. The search returns the best-scoring new child to simulate from.

**Fixed tree height.** A leaf at depth `height` is never expanded. Every visit to it runs another random playout from it instead. With `height = 1` this is flat Monte Carlo: only the root's moves are in the tree.

**Simulation.** The playout policy is uniformly random until the game ends.

**Back-propagation.** The result is added to every node on the path, flipped (1 − result) at each level, because consecutive levels belong to opposite players.

**Repeat.** `cycles` sets the number of select/expand/simulate/back-propagate loops. Every parameter (`cycles`, `expand`, `height`, `C`, `w`) and the random number generator can be passed to `monte_carlo_tree_search` and set from the command line.

### Test data

`test_connect4.py` holds the test positions: a win in one move, a position where O threatens to win so X must block, a trap position, a full-board draw, and winning lines in all four directions. The tests check the game rules, the objective function (symmetric, zero-sum, bounded, and preferring the centre), and the search: it takes the win, blocks the threat, avoids the trap, gives the same move for the same seed, with `expand=1` follows the objective function, and beats a random player as both X and O.

## Experiments

**Method.** All runs start from the base settings `cycles=1000, expand=7, height=4, C=1.4, w=1`, and each row changes one thing. Every cell is 20 independent searches (random seeds 0–19) on four positions, all with X to move:

```
Opening       Must block      Trap            Quiet midgame
.......       .......         .......         .......
.......       .......         .......         .......
.......       .......         .......         .......
.......       .......         X....O.         ...O...
.......       ..X....         OOO..X.         .O.XO.O
.......       .XXOOO.         OXX..X.         .X.XOXX
0123456       0123456         0123456         0123456
```

| Position | What a good move is | Why it is interesting |
|---|---|---|
| Opening | Column 3 (the centre is the solved best opening) | Columns 2, 3 and 4 have similar random-playout win rates |
| Must block | Column 6 (O has three in a row) | The objective function ranks column 2 (0.69) above the block (0.50) |
| Trap | Anything but column 3, because O wins by playing on top of it | Column 3 is the objective function's favourite (0.50) since it makes three in a row |
| Quiet midgame | No forced move; columns 4, 0 and 2 are close (objective scores 0.38, 0.10, 0.20) | Shows how consistent the generator is when no move stands out |

The tables give the percentage of the 20 runs that chose a good move. For the midgame they give how often each column was chosen (`4:15` means column 4 in 15 of the 20 runs). The ms/move column is the average time per search on an Apple Silicon Mac with Python 3.14. Each head-to-head match is 40 games with colours swapping every game, at 300 cycles per move unless the row says otherwise.

With 20 runs, one run is 5 points and the sampling noise on a percentage is about ±10 points, so only larger gaps mean anything.

### 1. Utility function

| C, w | Opening: centre % | Must block % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1.4, 0 | 90 | 100 | 100 | 4:15 0:3 2:2 | 88 |
| 1.4, 0.5 | 85 | 100 | 100 | 4:11 0:5 2:4 | 86 |
| 1.4, 1 | 75 | 100 | 100 | 4:9 0:6 2:5 | 85 |
| 1.4, 3 | 70 | 100 | 100 | 4:10 0:6 2:4 | 84 |
| 1.4, 10 | 85 | 100 | 100 | 0:15 2:4 4:1 | 79 |
| 0, 1 | 45 | 100 | 100 | 4:10 0:5 2:2 3:1 6:1 1:1 | 45 |
| 0.5, 1 | 85 | 100 | 100 | 4:16 0:3 2:1 | 69 |
| 3, 1 | 70 | 100 | 100 | 4:9 0:9 2:2 | 87 |

Same experiment with only 100 cycles:

| cycles, w | Opening: centre % | Must block % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 100, 0 | 30 | 80 | 55 | 2:7 4:6 0:6 1:1 | 18 |
| 100, 1 | 45 | 95 | 65 | 0:8 2:7 4:3 6:1 3:1 | 17 |
| 100, 3 | 40 | 85 | 80 | 4:10 2:7 0:3 | 16 |
| 100, 10 | 60 | 80 | 100 | 4:14 0:4 2:2 | 16 |

- **At 1,000 cycles the playout part dominates.** Every setting blocks and avoids the trap every time. The objective part fades as \(1/(N+1)\), so after a few dozen visits a node's score is almost all playout statistics. The opening differences (70–90%) are within noise.
- **At 100 cycles the objective part matters**, and it helps or hurts depending on whether the heuristic is right. Trap avoidance rises from 55% to 100% as \(w\) goes from 0 to 10, and the opening improves from 30% to 60%. The trap result is surprising, because the heuristic *likes* the trap move. The objective part also works one level down, though: O's winning reply on top of column 3 scores \(h = 1\) for O, so it is explored straight away and the trap is exposed. Blocking does not improve steadily (80, 95, 85, 80), because there the heuristic favours column 2 over the block.
- **Too much weight distorts the search.** With \(w = 10\) at 1,000 cycles, the quiet midgame switches to column 0 in 15 of 20 runs. With 5,000 cycles (table 2), every run picks column 4. The most likely cause is that the bias also picks O's replies, so the search trusts the heuristic's guess at O's best defence.
- **Exploration is needed.** With \(C = 0\) the search commits to whichever child had the luckiest early playouts. It has the worst opening (45%) and the widest midgame spread (6 different columns). It is also the fastest setting, because fewer new nodes get expanded and evaluated. \(C = 0.5\) was among the most consistent settings, and \(C = 3\) spread visits too evenly (midgame split 9/9 between columns 4 and 0).
- **Head-to-head:** \(w = 1\) vs \(w = 0\) finished 18 wins, 5 draws, 17 losses. At 300 cycles the objective part neither helps nor hurts overall playing strength.

### 2. Number of cycles

| cycles | Opening: centre % | Must block % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 25 | 25 | 55 | 80 | 4:7 2:6 0:4 3:2 5:1 | 4 |
| 50 | 35 | 30 | 60 | 2:9 0:6 4:4 3:1 | 8 |
| 100 | 45 | 95 | 65 | 0:8 2:7 4:3 6:1 3:1 | 17 |
| 250 | 60 | 100 | 100 | 0:8 2:7 4:5 | 40 |
| 500 | 75 | 100 | 100 | 4:8 0:6 2:6 | 60 |
| 1000 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |
| 2500 | 100 | 100 | 100 | 4:18 2:2 | 143 |
| 5000 | 100 | 100 | 100 | 4:20 | 239 |

- The number of cycles has the biggest effect of any setting. Below 100 cycles, each of the 7 root moves gets only a handful of playouts, and the choice is close to random (50 cycles blocked only 30% of the time).
- Positions with one clearly best move (block, trap) are solved by **250 cycles**. Close positions need far more: the opening reaches 100% only at 2,500 cycles, and the midgame becomes unanimous (column 4) only at 5,000. The noise in a playout average shrinks like \(1/\sqrt{N}\). Telling apart moves whose win rates differ by a few percent needs thousands of playouts, while a move that loses on the spot shows up in a few dozen.
- Time grows roughly linearly, at 0.05–0.08 ms per cycle. Later cycles are cheaper, because once the tree reaches its height limit they stop expanding nodes.
- **Head-to-head:** 1,000 cycles beat 300 cycles by 24 wins to 13, with 3 draws.

### 3. Expansion nodes x

| x | Opening: centre % | Must block % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1 | 100 | 0 | 0 | 4:20 | 20 |
| 2 | 100 | 60 | 100 | 4:18 2:2 | 32 |
| 3 | 100 | 100 | 100 | 4:20 | 37 |
| 4 | 90 | 100 | 100 | 4:17 0:2 2:1 | 44 |
| 5 | 90 | 100 | 100 | 4:8 2:7 0:5 | 53 |
| 7 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |

- **With x = 1 the tree is a single line**, so the move is simply the objective function's favourite. That is perfect where the heuristic is right (centre opening, 100%) and fatal where it is wrong (0% on both the block and the trap). The result is identical across all 20 seeds.
- **x = 2 shows randomness in expansion.** In the block position the heuristic's top choice is column 2, and columns 3 and 6 tie for second at 0.50. The random tie-break lets the blocking move into the tree in about half the runs, and when it is in the tree MCTS always picks it, which gives 60%.
- **x = 3 was the best setting:** 100% on every position, a unanimous midgame, and less than half the time of x = 7. Pruning to the heuristic's top 3 spends all the cycles on plausible moves, so the tree grows deeper on them.
- Larger x spreads the same budget over more weak moves, so results get noisier (the opening drops to 75%) and slower (more children to evaluate per expansion).
- The risk of small x is that a good move ranked below x by the heuristic can never be found, as the x = 1 and x = 2 rows show.
- **Head-to-head:** x = 3 beat x = 7 by 22 wins to 15, with 3 draws.

### 4. Tree height

| height | Opening: centre % | Must block % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1 | 80 | 95 | 100 | 4:10 0:7 2:3 | 37 |
| 2 | 90 | 100 | 100 | 4:14 0:6 | 38 |
| 3 | 85 | 100 | 100 | 0:8 4:8 2:4 | 43 |
| 4 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |
| 6 | 85 | 100 | 100 | 4:20 | 169 |
| 10 | 85 | 100 | 100 | 4:20 | 170 |
| 42 | 85 | 100 | 100 | 4:20 | 170 |

- **Height 1 (flat Monte Carlo) is decent on single positions** (95% block, 100% trap), because random playouts often stumble on O's immediate win. It is clearly weaker in real games, though: height 4 beat height 1 by 29 wins to 9. Without a tree, X never sees the opponent's best reply, only the average random reply.
- **Heights 6, 10 and 42 give identical results.** I measured how deep the tree actually grows: with 1,000 cycles it reaches depth 6–7 (about 7,000 nodes), and with 5,000 cycles depth 7–9. A cap of 6 or more almost never applies, and 42 means no limit.
- A deeper tree makes the quiet midgame unanimous (column 4, matching the 5,000-cycle answer), because values backed up through the tree are less noisy than raw playout averages.
- It also doubles the time (84 → 169 ms), because every cycle now expands a node and evaluates 7 children, while the playouts only get slightly shorter.
- **Head-to-head:** height 4 vs unlimited height finished 18 wins, 1 draw, 21 losses. That is no real difference at 300 cycles, where the tree stays shallow anyway.

### 5. Strength check

100-cycle MCTS beat the random player in **40 of 40** games.

## Reflection

### Does the simulator always generate the same move?

**With the same seed and settings, yes.** Every random choice comes from a seeded `random.Random`, so a run can be repeated exactly (`test_same_seed_gives_same_move`).

**Across different seeds, it depends on the position and the budget:**

- In positions with one clearly right move (a win, a forced block, a trap to avoid), it gives the same move in 20 of 20 runs once it has at least 250 cycles.
- In close positions (the opening, the quiet midgame) it often does not. At 1,000 cycles the midgame was split 9/6/5 between columns 4, 0 and 2. Only at 5,000 cycles, or with a deeper or narrower tree, did all 20 runs agree.

### What causes the differences

1. **Random playouts, the main cause.** A node's value is an average of random games. With \(N\) playouts the noise is about \(0.5/\sqrt{N}\), so at 1,000 cycles, when a root move has had around 150 playouts, the noise is about ±4%. If two moves are closer than that, the seed decides which one gets more visits.
2. **The random tie-break during expansion.** When x cuts through a tie, the seed decides which moves enter the tree at all (block position at x = 2: 60%).
3. **A small cycle budget.** Fewer playouts mean more noise, so 25–100 cycles gives near-random choices.
4. **High exploration (large C) or wide expansion (large x).** Both spread the budget over more moves, so each move's estimate is noisier.
5. **Choosing by visit count.** When two moves have similar values, their visit counts end up close and can swap places from one run to the next.

### What causes the similarities

1. **A large value gap.** A move that wins or loses immediately is separated from the rest within a few dozen playouts, and every run finds it.
2. **The objective part is deterministic.** The same board always gets the same score, so the more the search leans on it (small x, large w, few cycles), the more alike the runs are. In the extreme, x = 1 returns the heuristic's move every time, whether it is right or wrong. Consistent does not mean correct.
3. **More cycles and a deeper tree.** By the law of large numbers, estimates converge to the move's true value, and backing up values through the tree replaces noisy averages with something closer to minimax. At 5,000 cycles, or with a height of 6 or more, every seed agreed on column 4 in the midgame.

### Conclusions

The number of cycles matters most, then the expansion width x, then tree height. The objective part of the utility function matters only when the budget is small.

The best trade-off I found is **x = 3 with a height of about 4 and 1,000 cycles**. It was perfect on all four test positions, about 40 ms per move, and beat the x = 7 version head-to-head.

The objective function is a double-edged guide. It speeds up the search when it is right (centre openings, finding the opponent's immediate win) and can hide the right move when it is wrong (the block position at small x). The playout part is what corrects it, given enough cycles.

## Limitations

- The objective function is a simple count of open lines and ignores whose turn it is. It treats O's open three as one more line worth −16, not as a loss on the next move, which is why it misranks the block position.
- The playout policy is uniformly random. A policy that takes immediate wins and blocks would give much less noisy estimates per playout.
- The cycle count is fixed rather than time-based (IS-TIME-REMAINING in Figure 5.11). That makes runs reproducible, but the time per move varies with the position.
