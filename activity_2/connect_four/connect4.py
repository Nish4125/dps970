"""Connect Four move generator using Monte Carlo tree search (AIMA 4e, Figure 5.11)."""
import math
import random
from collections import namedtuple

ROWS, COLS = 6, 7
EMPTY = "."

# board: 42 cells, index row * COLS + col, row 0 is the bottom.
# utility: +1 if X has won, -1 if O has won, 0 otherwise.
State = namedtuple("State", "board to_move utility")

# every line of four cells on the board (69 of them)
WINDOWS = [
    [(r + i * dr) * COLS + c + i * dc for i in range(4)]
    for r in range(ROWS) for c in range(COLS)
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1))
    if 0 <= r + 3 * dr < ROWS and 0 <= c + 3 * dc < COLS
]
WEIGHT = (0, 1, 4, 16)  # value of an open window holding 0..3 of one player's pieces


def other(player):
    return "O" if player == "X" else "X"


class ConnectFour:
    """AIMA 4e Game interface: to_move, actions, result, is_terminal, utility."""

    initial = State((EMPTY,) * ROWS * COLS, "X", 0)

    def to_move(self, state):
        return state.to_move

    def actions(self, state):
        if state.utility:
            return []
        return [c for c in range(COLS) if state.board[(ROWS - 1) * COLS + c] == EMPTY]

    def result(self, state, col):
        b = state.board
        row = next(r for r in range(ROWS) if b[r * COLS + col] == EMPTY)
        i = row * COLS + col
        board = b[:i] + (state.to_move,) + b[i + 1:]
        utility = (1 if state.to_move == "X" else -1) if wins(board, row, col) else 0
        return State(board, other(state.to_move), utility)

    def is_terminal(self, state):
        return not self.actions(state)

    def utility(self, state, player):
        return state.utility if player == "X" else -state.utility


def wins(board, row, col):
    """Does the piece at (row, col) complete a line of four?"""
    p = board[row * COLS + col]
    for dr, dc in ((0, 1), (1, 0), (1, 1), (1, -1)):
        n = 1
        for s in (1, -1):
            r, c = row + s * dr, col + s * dc
            while 0 <= r < ROWS and 0 <= c < COLS and board[r * COLS + c] == p:
                n += 1
                r, c = r + s * dr, c + s * dc
        if n >= 4:
            return True
    return False


def evaluate(board, player):
    """Objective part of the utility: how good the board is for `player`, from the rules alone, in [-1, 1].

    Counts the lines of four each side can still complete, weighted by how full they are.
    Centre cells sit in more lines, so centre control is rewarded without a special rule.
    """
    score = 0
    for w in WINDOWS:
        cells = [board[i] for i in w]
        mine, theirs = cells.count(player), cells.count(other(player))
        if mine == 4:
            return 1.0
        if theirs == 4:
            return -1.0
        if not theirs:
            score += WEIGHT[mine]
        elif not mine:
            score -= WEIGHT[theirs]
    return math.tanh(score / 20)


class MCT_Node:
    """AIMA's MCT_Node, plus the node's depth and its objective score h."""

    def __init__(self, parent=None, state=None, h=0.0):
        self.parent, self.state, self.h = parent, state, h
        self.depth = parent.depth + 1 if parent else 0
        self.U = self.N = 0  # U: playout wins for the player who moved into this node
        self.children = {}  # child node -> action


def ucb(n, C=1.4, w=1.0):
    """Selection utility = playout part (UCB1) + objective part (progressive bias, fades as N grows)."""
    if n.N == 0:
        return math.inf
    return n.U / n.N + C * math.sqrt(math.log(n.parent.N) / n.N) + w * n.h / (n.N + 1)


def monte_carlo_tree_search(state, game, cycles=1000, expand=7, height=4, C=1.4, w=1.0, rng=random):
    """Figure 5.11. cycles: SELECT/EXPAND/SIMULATE/BACK-PROPAGATE loops; expand: children added per
    expanded node (best x by the objective score); height: depth below which the tree stops growing
    and leaves are scored by random playouts only."""

    def select(n):
        while n.children:
            n = max(n.children, key=lambda c: ucb(c, C, w))
        return n

    def expand_leaf(n):
        if n.depth >= height or game.is_terminal(n.state):
            return n
        player = game.to_move(n.state)
        kids = []
        for a in game.actions(n.state):
            s = game.result(n.state, a)
            kids.append((evaluate(s.board, player), rng.random(), a, s))  # random tie-break
        for h, _, a, s in sorted(kids, reverse=True)[:expand]:
            n.children[MCT_Node(n, s, h)] = a
        return next(iter(n.children))

    def simulate(state):
        player = other(game.to_move(state))  # the player who moved into this state
        while acts := game.actions(state):
            state = game.result(state, rng.choice(acts))
        return (game.utility(state, player) + 1) / 2  # win 1, draw 0.5, loss 0

    def back_propagate(result, n):
        while n:
            n.U += result
            n.N += 1
            result = 1 - result
            n = n.parent

    root = MCT_Node(state=state)
    for _ in range(cycles):
        leaf = select(root)
        child = expand_leaf(leaf)
        back_propagate(simulate(child.state), child)
    return root.children[max(root.children, key=lambda c: c.N)]


def random_player(game, state, rng=random):
    return rng.choice(game.actions(state))


def mcts_player(**params):
    return lambda game, state: monte_carlo_tree_search(state, game, **params)


def play_game(game, players, state=None, verbose=False):
    """AIMA play_game. players maps 'X'/'O' to functions (game, state) -> action."""
    state = state or game.initial
    while not game.is_terminal(state):
        move = players[game.to_move(state)](game, state)
        state = game.result(state, move)
        if verbose:
            print(f"{other(state.to_move)} plays {move}\n{show(state)}\n")
    return state


def parse(rows):
    """State from 6 strings, top row first, e.g. '..XO...'. Side to move comes from the piece counts."""
    if len(rows) != ROWS or any(len(r) != COLS or set(r) - {"X", "O", EMPTY} for r in rows):
        raise ValueError("need 6 rows of 7 characters from 'X', 'O', '.'")
    board = tuple("".join(reversed(rows)))
    xs, os_ = board.count("X"), board.count("O")
    if xs - os_ not in (0, 1):
        raise ValueError("X moves first, so X has as many pieces as O or one more")
    utility = 0
    for w in WINDOWS:
        if board[w[0]] != EMPTY and all(board[i] == board[w[0]] for i in w):
            utility = 1 if board[w[0]] == "X" else -1
    return State(board, "X" if xs == os_ else "O", utility)


def show(state):
    rows = ("".join(state.board[r * COLS:(r + 1) * COLS]) for r in reversed(range(ROWS)))
    return "\n".join(rows) + "\n0123456"


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="MCTS (X) plays a random player (O)")
    ap.add_argument("--cycles", type=int, default=1000)
    ap.add_argument("--expand", type=int, default=7)
    ap.add_argument("--height", type=int, default=4)
    ap.add_argument("--C", type=float, default=1.4)
    ap.add_argument("--w", type=float, default=1.0)
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()
    rng = random.Random(args.seed)
    mcts = mcts_player(cycles=args.cycles, expand=args.expand, height=args.height, C=args.C, w=args.w, rng=rng)
    final = play_game(ConnectFour(), {"X": mcts, "O": lambda g, s: random_player(g, s, rng)}, verbose=True)
    print({1: "X (MCTS) wins", -1: "O (random) wins", 0: "draw"}[final.utility])
