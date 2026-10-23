"""Three-jug problem solved with breadth-first search (AIMA 4th ed. Figure 3.9)."""
from collections import deque


class JugProblem:
    """State: tuple of gallons in each jug. Actions: ("fill", i), ("empty", i), ("pour", i, j)."""

    def __init__(self, capacities=(12, 8, 3), goal=1):
        self.capacities = tuple(capacities)
        self.goal = goal
        self.initial = (0,) * len(self.capacities)

    def actions(self, state):
        for i, amount in enumerate(state):
            if amount < self.capacities[i]:
                yield ("fill", i)
            if amount > 0:
                yield ("empty", i)
                for j in range(len(state)):
                    if j != i and state[j] < self.capacities[j]:
                        yield ("pour", i, j)

    def result(self, state, action):
        s = list(state)
        if action[0] == "fill":
            s[action[1]] = self.capacities[action[1]]
        elif action[0] == "empty":
            s[action[1]] = 0
        else:
            _, i, j = action
            moved = min(s[i], self.capacities[j] - s[j])
            s[i] -= moved
            s[j] += moved
        return tuple(s)

    def is_goal(self, state):
        return self.goal in state

    def action_cost(self, s, action, s1):
        return 1


class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state, self.parent, self.action, self.path_cost = state, parent, action, path_cost


def expand(problem, node):
    s = node.state
    for action in problem.actions(s):
        s1 = problem.result(s, action)
        cost = node.path_cost + problem.action_cost(s, action, s1)
        yield Node(s1, node, action, cost)


def path_actions(node):
    actions = []
    while node.parent is not None:
        actions.append(node.action)
        node = node.parent
    return actions[::-1]


def path_states(node):
    states = []
    while node is not None:
        states.append(node.state)
        node = node.parent
    return states[::-1]


def breadth_first_search(problem):
    """Returns a solution node, or None for failure."""
    node = Node(problem.initial)
    if problem.is_goal(node.state):
        return node
    frontier = deque([node])
    reached = {problem.initial}
    while frontier:
        node = frontier.popleft()
        for child in expand(problem, node):
            s = child.state
            if problem.is_goal(s):
                return child
            if s not in reached:
                reached.add(s)
                frontier.append(child)
    return None


def describe(problem, action):
    cap = problem.capacities
    if action[0] == "pour":
        return f"pour {cap[action[1]]}-gal jug into {cap[action[2]]}-gal jug"
    return f"{action[0]} {cap[action[1]]}-gal jug"


if __name__ == "__main__":
    problem = JugProblem()
    solution = breadth_first_search(problem)
    if solution is None:
        print("No solution.")
    else:
        states = path_states(solution)
        print(f"start {states[0]}")
        for action, state in zip(path_actions(solution), states[1:]):
            print(f"{describe(problem, action):35} -> {state}")
