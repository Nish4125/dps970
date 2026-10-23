Base settings: {'cycles': 1000, 'expand': 7, 'height': 4, 'C': 1.4, 'w': 1.0}. Each cell uses seeds 0..19; one setting is changed per row.

### Utility function (C = exploration weight, w = objective weight)

| C, w | Opening: centre % | Must block: col 6 % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1.4, 0 | 90 | 100 | 100 | 4:15 0:3 2:2 | 88 |
| 1.4, 0.5 | 85 | 100 | 100 | 4:11 0:5 2:4 | 86 |
| 1.4, 1 | 75 | 100 | 100 | 4:9 0:6 2:5 | 85 |
| 1.4, 3 | 70 | 100 | 100 | 4:10 0:6 2:4 | 84 |
| 1.4, 10 | 85 | 100 | 100 | 0:15 2:4 4:1 | 79 |
| 0, 1 | 45 | 100 | 100 | 4:10 0:5 2:2 3:1 6:1 1:1 | 45 |
| 0.5, 1 | 85 | 100 | 100 | 4:16 0:3 2:1 | 69 |
| 3, 1 | 70 | 100 | 100 | 4:9 0:9 2:2 | 87 |

### Utility function with only 100 cycles

| cycles, w | Opening: centre % | Must block: col 6 % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 100, 0 | 30 | 80 | 55 | 2:7 4:6 0:6 1:1 | 18 |
| 100, 1 | 45 | 95 | 65 | 0:8 2:7 4:3 6:1 3:1 | 17 |
| 100, 3 | 40 | 85 | 80 | 4:10 2:7 0:3 | 16 |
| 100, 10 | 60 | 80 | 100 | 4:14 0:4 2:2 | 16 |

### Number of cycles

| cycles | Opening: centre % | Must block: col 6 % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 25 | 25 | 55 | 80 | 4:7 2:6 0:4 3:2 5:1 | 4 |
| 50 | 35 | 30 | 60 | 2:9 0:6 4:4 3:1 | 8 |
| 100 | 45 | 95 | 65 | 0:8 2:7 4:3 6:1 3:1 | 17 |
| 250 | 60 | 100 | 100 | 0:8 2:7 4:5 | 40 |
| 500 | 75 | 100 | 100 | 4:8 0:6 2:6 | 60 |
| 1000 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |
| 2500 | 100 | 100 | 100 | 4:18 2:2 | 143 |
| 5000 | 100 | 100 | 100 | 4:20 | 239 |

### Expansion nodes x

| expand | Opening: centre % | Must block: col 6 % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1 | 100 | 0 | 0 | 4:20 | 20 |
| 2 | 100 | 60 | 100 | 4:18 2:2 | 32 |
| 3 | 100 | 100 | 100 | 4:20 | 37 |
| 4 | 90 | 100 | 100 | 4:17 0:2 2:1 | 44 |
| 5 | 90 | 100 | 100 | 4:8 2:7 0:5 | 53 |
| 7 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |

### Tree height

| height | Opening: centre % | Must block: col 6 % | Trap: avoids col 3 % | Quiet midgame: moves chosen | ms/move |
|---|---|---|---|---|---|
| 1 | 80 | 95 | 100 | 4:10 0:7 2:3 | 37 |
| 2 | 90 | 100 | 100 | 4:14 0:6 | 38 |
| 3 | 85 | 100 | 100 | 0:8 4:8 2:4 | 43 |
| 4 | 75 | 100 | 100 | 4:9 0:6 2:5 | 84 |
| 6 | 85 | 100 | 100 | 4:20 | 169 |
| 10 | 85 | 100 | 100 | 4:20 | 170 |
| 42 | 85 | 100 | 100 | 4:20 | 170 |

### Head-to-head (40 games, colours alternate, 300 cycles unless stated)

| Match (A vs B) | A wins | draws | B wins |
|---|---|---|---|
| w = 1 vs w = 0 | 18 | 5 | 17 |
| height 4 vs height 1 | 29 | 2 | 9 |
| height 4 vs height 42 | 18 | 1 | 21 |
| x = 3 vs x = 7 | 22 | 3 | 15 |
| 1000 cycles vs 300 cycles | 24 | 3 | 13 |
| 100-cycle MCTS (X) vs random player | 40 | - | 0 |
