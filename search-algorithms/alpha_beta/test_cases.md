# Alpha-Beta Test Cases

Alpha-Beta should return the same move quality as Minimax, while visiting fewer
nodes on many boards.

## Test Case 1 - Same Winning Move

```python
board = ["X", "X", " ",
         "O", "O", " ",
         " ", " ", " "]
```

Expected move: `2`

## Test Case 2 - Same Blocking Move

```python
board = ["O", "O", " ",
         "X", " ", " ",
         "X", " ", " "]
```

Expected move: `2`

## Test Case 3 - Pruning Evidence

The script records:

```python
stats = {"nodes": ..., "cutoffs": ...}
```

Expected result: `nodes > 0` and at least some positions should produce
`cutoffs > 0`, showing that pruning happened.
