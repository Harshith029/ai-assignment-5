# AI Assignment 5

This repository contains four parts:

1. Search algorithms
2. AI-based travel planner
3. Knowledge graphs and tools
4. Bayesian network modelling and inference

All code is written in plain Python and can be run without installing external
packages.

## Folder Structure

```text
AI_Assignments/
  README.md
  search-algorithms/
  travel-planner/
  knowledge-graphs/
  bayesian-network/
```

## 1. Search Algorithms

Folder: `search-algorithms/`

Implemented algorithms:

- Minimax search
- Alpha-Beta pruning
- Heuristic Alpha-Beta search
- Monte Carlo Tree Search

The implementation uses Tic-Tac-Toe as the game environment. The folder also
contains Markdown test-case files and a runnable unit test file.

Run demos:

```bash
cd search-algorithms
python minmax/minimax.py
python alpha_beta/alpha_beta.py
python heuristic_alpha_beta/heuristic_alpha_beta.py
python mcts/mcts.py
```

Run tests:

```bash
python test_search_algorithms.py
```

## 2. AI-Based Travel Planner

Folder: `travel-planner/`

The travel planner demonstrates:

- knowledge-base style entity storage,
- triple-style relationships,
- case-based reasoning,
- diet-aware food recommendation,
- wine/cuisine pairing,
- hotel selection,
- cost assessment.

Run:

```bash
cd travel-planner
python travel_planner.py
```

Documentation:

- `README.md` explains architecture, rules, CBR, and cost assessment.
- `test_cases.md` describes expected behavior for demo profiles.

## 3. Knowledge Graphs

Folder: `knowledge-graphs/`

This part describes:

- what knowledge graphs are,
- why they are useful,
- types of graph databases,
- tools used to build KGs,
- a mini university KG example,
- Cypher and RDF/SPARQL examples.

Read:

```text
knowledge-graphs/README.md
```

## 4. Bayesian Network

Folder: `bayesian-network/`

Implemented example:

```text
Rain -> Sprinkler
Rain -> WetGrass
Sprinkler -> WetGrass
```

The program performs exact inference by enumeration and demonstrates the
explaining-away effect.

Run:

```bash
cd bayesian-network
python bayesian_network.py
```

Documentation:

- `README.md` explains Bayesian networks, CPTs, tools, and inference.
- `test_cases.md` lists expected probabilities for the implemented queries.
