# MCTS Test Cases

MCTS is stochastic, so the test runner fixes the random seed before checking
the result.

## Test Case 1 - Immediate Win

```python
board = ["X", "X", " ",
         "O", "O", " ",
         " ", " ", " "]
player = "X"
simulations = 1000
```

Expected move: `2`

Reason: after enough simulations, the winning move should get the most visits.

## Test Case 2 - Statistics

Expected output includes one statistics row per explored root move:

```text
(move, visits, win_rate)
```

This supports correctness by showing how MCTS estimated each legal move.
