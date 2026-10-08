import unittest

from search import JugProblem, breadth_first_search, path_actions, path_states


def replay(problem, actions):
    state = problem.initial
    for action in actions:
        assert action in list(problem.actions(state)), (state, action)
        state = problem.result(state, action)
    return state


class TestTransitionModel(unittest.TestCase):
    p = JugProblem()

    def test_only_fills_from_empty(self):
        self.assertEqual(list(self.p.actions((0, 0, 0))), [("fill", 0), ("fill", 1), ("fill", 2)])

    def test_pour_stops_when_target_is_full(self):
        self.assertEqual(self.p.result((12, 0, 0), ("pour", 0, 1)), (4, 8, 0))
        self.assertEqual(self.p.result((4, 8, 0), ("pour", 0, 2)), (1, 8, 3))

    def test_pour_stops_when_source_is_empty(self):
        self.assertEqual(self.p.result((0, 2, 0), ("pour", 1, 2)), (0, 0, 2))

    def test_fill_and_empty(self):
        self.assertEqual(self.p.result((0, 5, 0), ("fill", 0)), (12, 5, 0))
        self.assertEqual(self.p.result((12, 5, 0), ("empty", 1)), (12, 0, 0))


class TestBreadthFirstSearch(unittest.TestCase):
    def test_finds_one_gallon_in_shortest_path(self):
        p = JugProblem()
        node = breadth_first_search(p)
        actions = path_actions(node)
        self.assertEqual(len(actions), 3)  # no 2-step plan leaves exactly 1 gallon
        self.assertIn(1, replay(p, actions))
        self.assertEqual(path_states(node)[-1], node.state)
        self.assertEqual(node.path_cost, 3)

    def test_every_amount_up_to_largest_jug_is_reachable(self):
        for goal in range(13):
            p = JugProblem(goal=goal)
            node = breadth_first_search(p)
            self.assertIsNotNone(node, goal)
            self.assertIn(goal, replay(p, path_actions(node)))

    def test_goal_already_true_at_start(self):
        node = breadth_first_search(JugProblem(goal=0))
        self.assertEqual(path_actions(node), [])

    def test_unreachable_goal_returns_failure(self):
        self.assertIsNone(breadth_first_search(JugProblem(capacities=(6, 4), goal=1)))  # gcd is 2
        self.assertIsNone(breadth_first_search(JugProblem(goal=13)))  # bigger than every jug


if __name__ == "__main__":
    unittest.main()
