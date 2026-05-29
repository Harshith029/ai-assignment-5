# Heuristic Alpha-Beta Test Cases

## Test Case 1 - Blocking Threat

```python
board = ["O", "O", " ",
         "X", " ", " ",
         "X", " ", " "]
```

Expected move: `2`

Reason: even with a depth limit, the search must avoid the immediate loss.

## Test Case 2 - Heuristic Evaluation

```python
board = ["X", " ", " ",
         " ", "O", " ",
         " ", " ", " "]
```

Expected behavior: moves that preserve more possible winning lines for `X`
should receive better heuristic scores.

## Test Case 3 - Depth Limit

The file uses:

```python
DEPTH_LIMIT = 4
```

Expected behavior: the algorithm returns quickly because it does not expand the
entire tree once the limit is reached.
