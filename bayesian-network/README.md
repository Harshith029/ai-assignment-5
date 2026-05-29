# Bayesian Network - Rain, Sprinkler, Wet Grass

## Objective

Explore tools for modelling, problem representation, and inference using
Bayesian Networks. Then implement one example.

The implemented example is the classic Rain, Sprinkler, Wet Grass network.

## What Is a Bayesian Network?

A Bayesian Network is a probabilistic graphical model. It represents variables
as nodes and direct dependencies as directed edges.

Each node has a probability table:

- a prior probability if it has no parents,
- a conditional probability table if it has parents.

The network must be a Directed Acyclic Graph.

## Example Network

```text
Rain ------> Sprinkler
  \              |
   \             v
    ----------> WetGrass
```

Variables:

| Variable | Meaning |
|---|---|
| `Rain` | Whether it rained |
| `Sprinkler` | Whether the sprinkler was on |
| `WetGrass` | Whether the grass is wet |

## Joint Probability

The full joint distribution factorizes as:

```text
P(Rain, Sprinkler, WetGrass)
= P(Rain) * P(Sprinkler | Rain) * P(WetGrass | Rain, Sprinkler)
```

This reduces the amount of probability data required compared to listing every
possible world manually.

## Probability Tables

### P(Rain)

| Rain | Probability |
|---|---|
| True | 0.20 |
| False | 0.80 |

### P(Sprinkler | Rain)

| Rain | P(Sprinkler=True) | P(Sprinkler=False) |
|---|---:|---:|
| True | 0.01 | 0.99 |
| False | 0.40 | 0.60 |

### P(WetGrass | Rain, Sprinkler)

| Rain | Sprinkler | P(Wet=True) | P(Wet=False) |
|---|---|---:|---:|
| True | True | 0.99 | 0.01 |
| True | False | 0.80 | 0.20 |
| False | True | 0.90 | 0.10 |
| False | False | 0.00 | 1.00 |

## Inference Method

The code uses exact inference by enumeration.

For a query such as:

```text
P(Rain | WetGrass=True)
```

the algorithm:

1. fixes the evidence,
2. tries both values of the target variable,
3. sums over all hidden variables,
4. normalizes the result.

## Queries Implemented

- `P(Rain | WetGrass=True)`
- `P(Sprinkler | WetGrass=True)`
- `P(Rain | WetGrass=True, Sprinkler=True)`

The third query demonstrates explaining away. If we already know the sprinkler
was on, the sprinkler explains the wet grass, so rain becomes less likely.

## Tools for Bayesian Networks

| Tool | Language | Use |
|---|---|---|
| pgmpy | Python | Modelling, inference, sampling, learning |
| bnlearn | R/Python | Structure learning and Bayesian-network analysis |
| pyAgrum | Python/C++ | Probabilistic graphical models and inference |
| GeNIe/SMILE | GUI/C++ | Bayesian-network modelling and decision support |
| Tetrad | Java | Causal discovery and graph modelling |
| BayesiaLab | GUI | Commercial Bayesian-network platform |

This implementation uses plain Python to show the inference logic directly.

## Run

```bash
python bayesian_network.py
```

## Expected Output

The output includes probabilities similar to:

```text
P(Rain | Wet=True)
  False: 0.6423
  True : 0.3577

P(Sprinkler | Wet=True)
  False: 0.3533
  True : 0.6467

P(Rain | Wet=True, Sprinkler=True)
  False: 0.9932
  True : 0.0068
```
