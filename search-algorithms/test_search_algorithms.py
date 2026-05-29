import importlib.util
import random
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load_module(name, relative_path):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


minimax = load_module("minimax_impl", "minmax/minimax.py")
alpha_beta = load_module("alpha_beta_impl", "alpha_beta/alpha_beta.py")
heuristic = load_module(
    "heuristic_alpha_beta_impl",
    "heuristic_alpha_beta/heuristic_alpha_beta.py",
)
mcts = load_module("mcts_impl", "mcts/mcts.py")


class SearchAlgorithmTests(unittest.TestCase):
    def test_minimax_finds_immediate_win(self):
        board = ["X", "X", " ", "O", "O", " ", " ", " ", " "]
        move, score = minimax.best_move(board, "X")
        self.assertEqual(move, 2)
        self.assertEqual(score, 10)

    def test_minimax_blocks_opponent(self):
        board = ["O", "O", " ", "X", " ", " ", "X", " ", " "]
        move, _score = minimax.best_move(board, "X")
        self.assertEqual(move, 2)

    def test_alpha_beta_matches_minimax_move(self):
        board = ["X", "O", " ", " ", "X", " ", "O", " ", " "]
        mm_move, _ = minimax.best_move(board[:], "X")
        ab_move, _score, stats = alpha_beta.best_move(board[:], "X")
        self.assertEqual(ab_move, mm_move)
        self.assertGreater(stats["nodes"], 0)

    def test_heuristic_alpha_beta_handles_block(self):
        board = ["O", "O", " ", "X", " ", " ", "X", " ", " "]
        move, _score = heuristic.best_move(board)
        self.assertEqual(move, 2)

    def test_mcts_prefers_winning_move_with_fixed_seed(self):
        board = ["X", "X", " ", "O", "O", " ", " ", " ", " "]
        random.seed(7)
        move, stats = mcts.mcts(board, "X", simulations=1000)
        self.assertEqual(move, 2)
        self.assertTrue(stats)


if __name__ == "__main__":
    unittest.main(verbosity=2)
