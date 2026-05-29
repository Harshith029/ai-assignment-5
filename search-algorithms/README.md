# AI Search Algorithms - Tic-Tac-Toe

This folder implements four adversarial search algorithms on Tic-Tac-Toe:

- Minimax search
- Alpha-Beta pruning
- Heuristic Alpha-Beta search
- Monte Carlo Tree Search

The board is a Python list of nine cells. `X` is the maximizing player, `O` is
the minimizing player, and a single space `" "` means the cell is empty.

```text
0 | 1 | 2
3 | 4 | 5
6 | 7 | 8
```

## Folder Structure

```text
search-algorithms/
  README.md
  test_search_algorithms.py
  minmax/
    minimax.py
    test_cases.md
  alpha_beta/
    alpha_beta.py
    test_cases.md
  heuristic_alpha_beta/
    heuristic_alpha_beta.py
    test_cases.md
  mcts/
    mcts.py
    test_cases.md
```

## Algorithms

### Minimax

Minimax explores the complete game tree. At `X` turns it chooses the maximum
score, and at `O` turns it chooses the minimum score. Terminal boards are scored
as:

```text
X win  -> +10
O win  -> -10
Draw   -> 0
```

This guarantees optimal play for Tic-Tac-Toe because the full state space is
small enough to search completely.

### Alpha-Beta Pruning

Alpha-Beta search gives the same decision as minimax but avoids exploring
branches that cannot affect the final answer. It keeps two bounds:

- `alpha`: best value already found for the maximizing player,
- `beta`: best value already found for the minimizing player.

When `alpha >= beta`, the remaining branch is pruned.

### Heuristic Alpha-Beta

Heuristic Alpha-Beta uses the same pruning idea, but it stops at a fixed depth
and estimates unfinished boards. The heuristic rewards lines still open for
`X` and penalizes lines still open for `O`.

This is useful for games where the full tree is too large. Tic-Tac-Toe is small,
but the method demonstrates the idea clearly.

### Monte Carlo Tree Search

MCTS uses repeated random simulations. Each simulation has four phases:

1. Selection using UCT.
2. Expansion of an unvisited move.
3. Rollout to a terminal board.
4. Backpropagation of win/draw/loss information.

The final action is the child of the root with the most visits.

## Run Demos

```bash
python minmax/minimax.py
python alpha_beta/alpha_beta.py
python heuristic_alpha_beta/heuristic_alpha_beta.py
python mcts/mcts.py
```

## Run Test Cases

```bash
python test_search_algorithms.py
```

The tests check immediate wins, blocking moves, Alpha-Beta agreement with
Minimax, heuristic blocking, and MCTS behavior with a fixed random seed.
