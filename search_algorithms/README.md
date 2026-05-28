# Search Algorithms (Part 1)

Minimax, alpha-beta, heuristic alpha-beta (depth-limited with an
evaluation function), and MCTS (UCT). Tested on TicTacToe and
Connect-Four.

## Files

- `games.py` - TicTacToe and ConnectFour classes; both expose the same
  `actions / result / terminal / utility / to_move / hash` interface.
  ConnectFour also has a `heuristic()` method used by heuristic AB.
- `search.py` - the four algorithms. Each returns `(action, stats)`.
- `test_search.py` - 15 unit tests + a `--demo` mode.
- `demo_output.txt` - sample run of the demo.

## Run

```
python -m unittest test_search -v
python test_search.py --demo
```

## Notes

**Minimax.** Plain recursive minimax. Used as a baseline / correctness
oracle on small games.

**Alpha-beta.** Same value as minimax with pruning. On TicTacToe from
the empty board it explores about 3.3% of the nodes minimax does.

**Heuristic alpha-beta.** Depth-limited, with a static evaluator at
the leaves. The ConnectFour heuristic slides a 4-cell window across
the board, scoring live threes / twos / ones, plus a small center
bonus. Move ordering (sort children by their immediate heuristic
before recursing) gives a big speedup on C4.

**MCTS / UCT.** Standard four-phase loop (select, expand, simulate,
backpropagate) with UCB1 selection. Two things to be careful about:
- backup flips the sign at opponent nodes so UCT's "best child"
  always picks the move best for the player about to move
- the root returns the most-visited child, not the highest win rate
  (more stable when rollouts are few)

## What the tests check

- Tactical positions: each algorithm finds the obvious win or block.
- Value equivalence: alpha-beta agrees with minimax on multiple TTT
  positions (`test_same_value_as_minimax`).
- TTT under optimal play draws (minimax vs minimax, AB vs AB,
  AB vs minimax).
- Pruning works: AB explores strictly fewer nodes than minimax on the
  empty board.
- Strength: heuristic AB d=4 beats random 6/6 on C4; MCTS 1500 wins
  4/4 on C4.
- Both heuristic AB (d=5) and MCTS (2000 rollouts) pick column 3 as
  the C4 opening move (the known optimum).

## Sample output (from `demo_output.txt`)

```
minimax vs alpha-beta (TicTacToe, empty board)
  minimax   : 549946 nodes (982.7 ms)
  alphabeta : 18297 nodes (35.8 ms)
  ratio     : 3.3%

heuristic AB d=5 on C4 opening
  pick col 3  nodes=1129 cutoffs=196 (162 ms)

MCTS 2000 rollouts on C4 opening
  pick col 3  (1435 ms)
```
