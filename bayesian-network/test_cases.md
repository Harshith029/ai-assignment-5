# Bayesian Network Test Cases

## Test Case 1 - Rain Given Wet Grass

Query:

```python
query("rain", {"wet": True})
```

Expected result:

```text
P(Rain=True | Wet=True) approximately 0.3577
```

## Test Case 2 - Sprinkler Given Wet Grass

Query:

```python
query("sprinkler", {"wet": True})
```

Expected result:

```text
P(Sprinkler=True | Wet=True) approximately 0.6467
```

## Test Case 3 - Explaining Away

Query:

```python
query("rain", {"wet": True, "sprinkler": True})
```

Expected result:

```text
P(Rain=True | Wet=True, Sprinkler=True) approximately 0.0068
```

Interpretation: once the sprinkler is known to be on, rain becomes a much less
likely explanation for wet grass.
