# Knowledge Graphs (Part 3)

Builds a small working knowledge graph from `data/facts.csv`, persists it
as Turtle, queries it with SPARQL, runs OWL-RL inference, exports an
interactive PyVis graph, and includes runnable snippets comparing
RDFLib, NetworkX, and Neo4j.

The original survey document is `knowledge_graphs.md`. This README is
for the working implementation.

## Files

- `kg.py` - complete build/query/reason/export script.
- `data/facts.csv` - small CSV of real Indian places, monuments,
  rulers and dynasties.
- `kg.ttl` - Turtle export produced from the CSV + schema.
- `graph.html` - interactive graph visualisation.
- `test_kg.py` - 8 unit tests for build counts, SPARQL, inference,
  export, and tool demos.
- `demo_output.txt` - sample run of `python kg.py`.

## Run

```
pip install rdflib owlrl pyvis networkx neo4j
python kg.py
python -m unittest test_kg -v
```

`neo4j` is optional at runtime. If `NEO4J_URI`, `NEO4J_USER`, and
`NEO4J_PASSWORD` are set, `kg.py` runs a tiny driver connectivity
query; otherwise it prints the Cypher load snippet without requiring a
server.

## What a KG is

A knowledge graph stores facts as typed relationships between entities:

```
(Charminar, locatedIn, Hyderabad)
(Hyderabad, locatedIn, Telangana)
(Telangana, locatedIn, India)
```

The ontology/schema gives the facts meaning. In this project the schema
contains classes (`Place`, `Monument`, `Person`, `Dynasty`) and
relations (`locatedIn`, `capitalOf`, `builtBy`, `dynasty`). It also says
`locatedIn` is transitive and `capitalOf` is a sub-property of
`locatedIn`, so reasoning can infer facts like:

```
Charminar locatedIn India
Jaipur locatedIn India
```

## Tool comparison

| Tool | Demo in code | Best use |
|---|---|---|
| RDFLib | `rdflib_demo()` runs SPARQL on RDF triples | Standards-based semantic graphs, Turtle/RDF, SPARQL |
| NetworkX | `networkx_demo()` converts triples to a Python graph and finds a path | Graph algorithms and quick in-memory analysis |
| Neo4j | `neo4j_optional_demo()` uses the Python driver in a guarded block | App-facing property graphs with Cypher |

## What the tests check

- Exact pre-inference triple count from the CSV + schema.
- Turtle export writes a real file.
- SPARQL returns the expected Hyderabad monuments.
- Property paths find India before reasoning.
- OWL-RL inference adds direct `locatedIn India` triples.
- Post-inference SPARQL sees the materialised facts.
- PyVis HTML export contains graph content.
- The rdflib / networkx / neo4j comparison snippets run.
