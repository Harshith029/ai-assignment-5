# AI Assignment 5

Four parts:

1. **Search algorithms** (`search_algorithms/`) - minimax, alpha-beta,
   heuristic alpha-beta, MCTS. Code + tests.
2. **AI travel planner** (`travel_planner/`) - owlready2 + W3C wine
   ontology, OWL/SWRL-style reasoning, budgeted itinerary generation,
   CLI + tests.
3. **Knowledge graphs** (`knowledge_graphs/`) - rdflib KG build from
   CSV, SPARQL, OWL-RL inference, PyVis export, tool demos + tests.
4. **Bayesian networks** (`bayesian_networks/`) - tool survey + a
   working pgmpy implementation of the burglar/alarm network.

## Quick test

```
pip install -r requirements.txt

# Part 1
cd search_algorithms
python -m unittest test_search -v
python test_search.py --demo

# Part 2
cd ../travel_planner
python -m unittest test_planner -v
python planner.py --destination Tuscany --budget 1500 --days 5 \
    --interests Heritage,WineTour,Food --group couple --diet Vegetarian

# Part 3
cd ../knowledge_graphs
python -m unittest test_kg -v
python kg.py

# Part 4
cd ../bayesian_networks
python bayes_alarm.py
```
