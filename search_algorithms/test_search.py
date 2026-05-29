import random
import time
import unittest

from games import TicTacToe, ConnectFour, TTTState
from search import minimax, alphabeta, heuristic_alphabeta, mcts


def play_match(game, agent_x, agent_o, start_state=None, verbose=False):
    state = start_state if start_state is not None else game.initial_state()
    agents = {game.to_move(state): agent_x}
    first = game.to_move(state)
    if first == "X":
        other = "O"
    elif first == "R":
        other = "Y"
    else:
        other = "X"
    agents[other] = agent_o

    while not game.terminal(state):
        p = game.to_move(state)
        a = agents[p](game, state)
        state = game.result(state, a)
        if verbose:
            print(f"\n{p} plays {a}")
            print(state)

    first_player = "X" if isinstance(game, TicTacToe) else "R"
    return game.utility(state, first_player), state


def random_agent(game, state):
    return random.choice(game.actions(state))


def minimax_agent(game, state):
    a, _ = minimax(game, state)
    return a


def ab_agent(game, state):
    a, _ = alphabeta(game, state)
    return a


def hab_agent(depth):
    def agent(game, state):
        a, _ = heuristic_alphabeta(game, state, depth=depth)
        return a
    return agent


def mcts_agent(iters):
    def agent(game, state):
        a, _ = mcts(game, state, iterations=iters)
        return a
    return agent


def _solve(game, state, original_player):
    if game.terminal(state):
        return game.utility(state, original_player)
    if game.to_move(state) == original_player:
        return max(_solve(game, game.result(state, a), original_player)
                   for a in game.actions(state))
    return min(_solve(game, game.result(state, a), original_player)
               for a in game.actions(state))


class TestMinimax(unittest.TestCase):

    def test_immediate_win(self):
        ttt = TicTacToe()
        s = TTTState(board=("X", "X", ".", "O", "O", ".",
                            ".", ".", "."), to_move="X")
        a, stats = minimax(ttt, s)
        self.assertEqual(a, 2)
        self.assertGreater(stats["nodes"], 0)

    def test_block(self):
        ttt = TicTacToe()
        s = TTTState(board=("O", "O", ".", ".", "X", ".",
                            ".", ".", "."), to_move="X")
        a, _ = minimax(ttt, s)
        self.assertEqual(a, 2)

    def test_optimal_play_is_draw(self):
        ttt = TicTacToe()
        util, _ = play_match(ttt, minimax_agent, minimax_agent)
        self.assertEqual(util, 0)


class TestAlphaBeta(unittest.TestCase):

    def test_same_value_as_minimax(self):
        ttt = TicTacToe()
        positions = [
            TTTState(board=tuple("." * 9), to_move="X"),
            TTTState(board=("X", ".", ".", ".", "O", ".",
                            ".", ".", "."), to_move="X"),
            TTTState(board=("X", "O", ".", ".", "X", ".",
                            ".", ".", "O"), to_move="X"),
        ]
        for s in positions:
            mm_action, _ = minimax(ttt, s)
            ab_action, _ = alphabeta(ttt, s)
            mm_value = _solve(ttt, ttt.result(s, mm_action), s.to_move)
            ab_value = _solve(ttt, ttt.result(s, ab_action), s.to_move)
            self.assertEqual(mm_value, ab_value,
                             f"AB and minimax disagree on {s.board}")

    def test_alphabeta_explores_fewer_nodes(self):
        ttt = TicTacToe()
        s = ttt.initial_state()
        _, mm_stats = minimax(ttt, s)
        _, ab_stats = alphabeta(ttt, s)
        self.assertLess(ab_stats["nodes"], mm_stats["nodes"])

    def test_optimal_play_is_draw(self):
        ttt = TicTacToe()
        util, _ = play_match(ttt, ab_agent, ab_agent)
        self.assertEqual(util, 0)

    def test_alphabeta_vs_minimax_is_draw(self):
        ttt = TicTacToe()
        util, _ = play_match(ttt, ab_agent, minimax_agent)
        self.assertEqual(util, 0)
        util, _ = play_match(ttt, minimax_agent, ab_agent)
        self.assertEqual(util, 0)


class TestHeuristicAlphaBeta(unittest.TestCase):

    def test_immediate_win_connect4(self):
        c4 = ConnectFour()
        state = c4.initial_state()
        for col in [3, 0, 4, 1, 5]:
            state = c4.result(state, col)
        a, _ = heuristic_alphabeta(c4, state, depth=2)
        self.assertIn(a, [2, 6])

    def test_blocks_opponent_win(self):
        c4 = ConnectFour()
        s = c4.initial_state()
        for col in [0, 3, 1, 4, 0, 5]:
            s = c4.result(s, col)
        a, _ = heuristic_alphabeta(c4, s, depth=3)
        self.assertIn(a, [2, 6])

    def test_beats_random_on_connect4(self):
        c4 = ConnectFour()
        wins = 0
        N = 6
        for i in range(N):
            random.seed(i)
            util, _ = play_match(c4, hab_agent(depth=4), random_agent)
            if util > 0:
                wins += 1
        self.assertGreaterEqual(wins, N - 1)

    def test_move_ordering_actually_helps(self):
        c4 = ConnectFour()
        s = c4.initial_state()
        _, stats = heuristic_alphabeta(c4, s, depth=4)
        self.assertGreater(stats["cutoffs"], 0)


class TestMCTS(unittest.TestCase):

    def test_mcts_finds_immediate_win_tictactoe(self):
        ttt = TicTacToe()
        s = TTTState(board=("X", "X", ".", "O", "O", ".",
                            ".", ".", "."), to_move="X")
        random.seed(42)
        a, stats = mcts(ttt, s, iterations=500)
        self.assertEqual(a, 2)
        self.assertGreater(stats["rollouts"], 0)

    def test_mcts_beats_random_tictactoe(self):
        ttt = TicTacToe()
        losses = 0
        for i in range(10):
            random.seed(i)
            util, _ = play_match(ttt, mcts_agent(500), random_agent)
            if util < 0:
                losses += 1
        self.assertEqual(losses, 0)

    def test_mcts_beats_random_connect4(self):
        c4 = ConnectFour()
        wins = 0
        for i in range(4):
            random.seed(i)
            util, _ = play_match(c4, mcts_agent(1500), random_agent)
            if util > 0:
                wins += 1
        self.assertGreaterEqual(wins, 3)

    def test_mcts_vs_minimax_tictactoe_is_draw(self):
        ttt = TicTacToe()
        random.seed(0)
        util, _ = play_match(ttt, mcts_agent(2000), minimax_agent)
        self.assertLessEqual(util, 0)
        util, _ = play_match(ttt, minimax_agent, mcts_agent(2000))
        self.assertGreaterEqual(util, 0)


def demo():
    ttt = TicTacToe()
    s = ttt.initial_state()
    t0 = time.time(); _, mm = minimax(ttt, s);   t_mm = time.time() - t0
    t0 = time.time(); _, ab = alphabeta(ttt, s); t_ab = time.time() - t0
    print("minimax vs alpha-beta (TicTacToe, empty board)")
    print(f"  minimax   : {mm['nodes']} nodes ({t_mm*1000:.1f} ms)")
    print(f"  alphabeta : {ab['nodes']} nodes ({t_ab*1000:.1f} ms)")
    print(f"  ratio     : {ab['nodes']/mm['nodes']:.1%}")

    c4 = ConnectFour()
    s = c4.initial_state()
    t0 = time.time(); a, st = heuristic_alphabeta(c4, s, depth=5)
    t_h = time.time() - t0
    print(f"\nheuristic AB d=5 on C4 opening")
    print(f"  pick col {a}  nodes={st['nodes']} cutoffs={st['cutoffs']} "
          f"({t_h*1000:.0f} ms)")

    random.seed(0)
    t0 = time.time(); a, st = mcts(c4, s, iterations=2000)
    t_m = time.time() - t0
    print(f"\nMCTS 2000 rollouts on C4 opening")
    print(f"  pick col {a}  ({t_m*1000:.0f} ms)")
    for action, visits, winrate in sorted(st["root_children"], key=lambda x: -x[1]):
        print(f"  col {action}: {visits:>4} visits  winrate {winrate:+.2f}")


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        demo()
    else:
        unittest.main(verbosity=2)
