# AI Assignment 5

Four parts:

1. **Search algorithms** (`search_algorithms/`) - minimax, alpha-beta,
   heuristic alpha-beta, MCTS. Code + tests.
2. **AI travel planner** (`travel_planner/`) - design that reuses
   existing knowledge bases (Wikidata, OSM, Stanford wine ontology,
   FoodOn, etc.) with CBR for personalisation.
3. **Knowledge graphs** (`knowledge_graphs/`) - description + tool
   survey.
4. **Bayesian networks** (`bayesian_networks/`) - tool survey + a
   working pgmpy implementation of the burglar/alarm network.

## Quick test

```
# Part 1
cd search_algorithms
python -m unittest test_search -v
python test_search.py --demo

# Part 4
cd ../bayesian_networks
pip install pgmpy
python bayes_alarm.py
```

Parts 2 and 3 are markdown design documents only.
