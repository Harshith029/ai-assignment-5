# Minimax Test Cases

## Test Case 1 - Immediate Win

```python
board = ["X", "X", " ",
         "O", "O", " ",
         " ", " ", " "]
player = "X"
```

Expected move: `2`

Reason: placing `X` at index `2` completes the top row.

## Test Case 2 - Block Opponent

```python
board = ["O", "O", " ",
         "X", " ", " ",
         "X", " ", " "]
player = "X"
```

Expected move: `2`

Reason: `O` is threatening the top row, so `X` must block.

## Test Case 3 - Empty Board

```python
board = [" ", " ", " ",
         " ", " ", " ",
         " ", " ", " "]
player = "X"
```

Expected result: draw score `0` with optimal play.
