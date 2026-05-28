# Knowledge Graphs (Part 3)

Describes Knowledge Graphs and the tools to build them. Builds on the
tool list shared with the assignment, with a few additions from things
I've used or read about.

## 1. What is a Knowledge Graph?

A **knowledge graph (KG)** is a graph of real-world entities (the nodes)
connected by typed semantic relationships (the edges), where both nodes
and edges have an explicit, machine-readable meaning. Formally:

> KG = (E, R, F) - a set of **entities** E, **relations** R, and
> **facts** F, where each fact is a triple `(head, relation, tail)`.

Example triples about Hyderabad:

```
(Hyderabad, capitalOf, Telangana)
(Hyderabad, locatedIn, India)
(Charminar, locatedIn, Hyderabad)
(Charminar, builtBy, Quli_Qutb_Shah)
(Quli_Qutb_Shah, dynasty, Qutb_Shahi)
```

The schema itself - which entity types and relations exist - is part of
the graph. That's the ontology, or TBox. It lets you do simple inference
like "Charminar is located in India" without that triple being stored.

## 2. How a KG differs from things people confuse it with

| Concept | Difference from a KG |
|---|---|
| Relational DB | RDB schema is closed and predefined. A KG schema is open, extensible, and the relations carry semantic meaning. |
| Property graph (Neo4j default) | KG usually has an explicit ontology and global URIs. Property graphs often only have local labels. |
| RDF triple store | RDF is one encoding of a KG. Not every KG is RDF - Neo4j, JanusGraph, TigerGraph are property-graph KGs. |
| Vector embedding store | A KG stores symbolic facts you can query exactly. A vector store does fuzzy similarity. The best modern systems combine both (RAG over a KG). |

## 3. Anatomy of a modern KG

1. **Ontology / Schema (TBox)** - class hierarchy, relation signatures,
   axioms. Written in OWL (or sometimes SHACL).
2. **Instance data (ABox)** - the actual triples.
3. **Reasoner** - derives implicit facts from the ontology + data.
   HermiT, Pellet, ELK.
4. **Query interface** - SPARQL for RDF; Cypher or Gremlin for property
   graphs.
5. **Embedding layer** (optional) - TransE, ComplEx, RotatE, or GNN-based
   encoders for link prediction and similarity.
6. **Ingestion pipeline** - NER + entity linking + relation extraction
   to turn raw text into triples.

## 4. Construction pipeline (typical)

```
unstructured text + structured sources
            |
            v
   NER (spaCy, Flair, GLiNER)
            |
            v
   Entity Linking (REL, BLINK, GENRE) -> link to Wikidata QIDs
            |
            v
   Relation Extraction (REBEL, OpenIE, LLM extraction)
            |
            v
   Schema mapping + deduplication
            |
            v
   Triple store / property graph
            |
            v
   Reasoner (HermiT) -> materialised inferences
            |
            v
   Query / serve  (SPARQL endpoint, Cypher, GraphQL)
```

## 5. Tools (built on the instructor's list, plus a few additions)

### 5.1 Graph databases - storage and querying

| Tool | Type | Notes |
|---|---|---|
| **Neo4j** | property graph | The most common pick. Cypher query language, huge ecosystem, lots of AI integrations. |
| **Memgraph** | property graph, in-memory | Faster for streaming use cases. Cypher-compatible. |
| **Amazon Neptune** | both RDF and property graph | Managed AWS service, scales without ops. |
| **Azure Cosmos DB** | multi-model incl. graph | Managed Azure service. |
| **AllegroGraph** | RDF triple store | Strong on semantic web / RDF. |
| **GraphDB (Ontotext)** | RDF triple store | Built-in reasoner, free tier. |
| **JanusGraph** | property graph, distributed | Designed for very large datasets, runs on Cassandra/HBase. |
| **Apache Jena Fuseki** | RDF | Open source, easy SPARQL endpoint. |
| **Stardog** | RDF + virtual graphs | Strong reasoning, federated queries. |
| **Blazegraph** | RDF | What powers the Wikidata Query Service. |
| **Virtuoso** | RDF | What powers DBpedia. |
| **TigerGraph** | property graph | Fast on very large graphs. |
| **ArangoDB** | multi-model | Document + graph in one. |

Picking among these:
- **Massive, distributed dataset** -> JanusGraph (or one of the managed
  services).
- **Strict semantic / standards-based data** -> a triple store (RDF), so
  AllegroGraph, GraphDB, Stardog, Jena.
- **Flexible, highly relational application data** -> a property graph,
  so Neo4j or Memgraph.

### 5.2 Constructing / automating graphs (unstructured -> structured)

| Tool | What it does |
|---|---|
| **LlamaIndex / LangChain** | Frameworks that wrap LLMs to ingest documents and extract entities + relations. The "low-code" option. |
| **GliNER** | Zero-shot named entity recognition - works without training data. Lightweight. |
| **Infranodus** | Online tool (and Obsidian extension) for building KGs from text with LLM assistance. |
| **ContextClue Graph Builder** | Specialised for extracting knowledge from PDFs and tables. |
| **spaCy** | Classical NER + dependency parsing. Still the workhorse for production NER. |
| **REBEL** (Hugging Face) | End-to-end relation extraction; outputs triples directly. |
| **OpenIE 6** | Open-domain triple extraction. |
| **DeepKE** | A toolkit covering NER, relation extraction, and entity linking together. |

### 5.3 Ontology and modelling tools

| Tool | What it's for |
|---|---|
| **Protégé** | Open-source GUI editor for OWL ontologies. The industry standard. |
| **WebProtégé** | Browser-based collaborative ontology editing. |
| **TopBraid Composer** | Commercial modelling environment for RDF/OWL ontologies. Better team workflows than Protégé. |
| **OWLready2 (Python)** | Programmatic ontology editing + reasoning from Python. |

### 5.4 Reasoners

| Reasoner | Best for |
|---|---|
| **HermiT** | OWL 2 DL, complete and sound. |
| **Pellet** | OWL DL, has good debugging / explanation support. |
| **ELK** | OWL 2 EL profile - extremely fast on biomedical ontologies (SNOMED CT, Gene Ontology). |
| **RDFox** | High-performance Datalog + SWRL rules engine. |

### 5.5 Visualization

| Tool | Notes |
|---|---|
| **Gephi** | Open-source, very flexible for visualising and analysing large graph networks. |
| **Kumu** | Web-based, friendly for non-technical users mapping relationships. |
| **Linkurious** | Specifically for exploring Neo4j data interactively. |
| **Neo4j Bloom** | Neo4j's own visual exploration UI. |
| **yEd** | General graph editor; good for diagrams of small KGs. |

### 5.6 Personal KGs

| Tool | Notes |
|---|---|
| **Obsidian Graph View** | Markdown notes plus an automatic graph of links between them. Great for personal knowledge work. |
| **TheBrain** | Long-term, hierarchical, associative note taking. |
| **Logseq** | Similar to Obsidian; block-based outliner with a graph view. |

### 5.7 Embedding libraries (for link prediction etc.)

| Library | Algorithms |
|---|---|
| **PyKEEN** | 40+ KG embedding models, benchmarking, hyperparameter search. |
| **AmpliGraph** | TransE, ComplEx, DistMult; TF-based. |
| **DGL-KE** | Distributed training on huge KGs (Wikidata scale). |
| **PyG (PyTorch Geometric)** | GNNs over KGs - R-GCN, CompGCN, etc. |

### 5.8 Public KGs you can reuse

| KG | Size | What it's good for |
|---|---|---|
| **Wikidata** | ~110M entities, billions of triples | General world knowledge, free SPARQL endpoint. |
| **DBpedia** | ~6M entities | Wikipedia-derived, well documented. |
| **YAGO 4.5** | ~50M | Cleaned Wikidata + WordNet alignment. |
| **ConceptNet** | ~8M nodes | Commonsense relations. |
| **Wikifier / BabelNet** | multilingual | Word-sense disambiguation. |
| **Google Knowledge Graph API** | closed | Search-time entity resolution. |
| **UMLS, SNOMED CT, Gene Ontology** | biomedical | Healthcare AI. |

## 6. Query languages compared

**SPARQL** (RDF):
```sparql
SELECT ?city WHERE {
  ?city wdt:P31 wd:Q515 ;     # instance of city
        wdt:P17 wd:Q668 .     # country = India
}
```

**Cypher** (property graph, Neo4j):
```cypher
MATCH (c:City)-[:LOCATED_IN]->(:Country {name: 'India'})
RETURN c.name
```

**Gremlin** (Apache TinkerPop):
```groovy
g.V().hasLabel('City').out('LOCATED_IN').has('name', 'India')
```

## 7. Practical build recipes

For a small / personal KG (~1k entities):
RDFLib + Protégé. SQLite-backed store. SPARQL via RDFLib.

For a medium internal product KG (~1M entities):
Neo4j (community edition) + spaCy for NER + LLM-assisted relation
extraction. Cypher queries. APOC plugin for graph algorithms.

For a large research KG (100M+ entities):
Apache Jena TDB or GraphDB free. Periodic Wikidata dumps in HDT
(compressed RDF) format. Fuseki SPARQL endpoint. PyKEEN for embeddings.

For production at scale:
Stardog or Amazon Neptune. Separate vector store (Pinecone, Weaviate,
or pgvector) for hybrid symbolic + semantic search.

## 8. Common failure modes

1. **Schema drift.** Different sources use different identifiers for the
   same entity (Hyderabad vs Hyderabad vs Q15340). Fix by strictly
   linking everything to Wikidata QIDs.
2. **Reasoning blow-up.** OWL DL reasoners can get very slow or
   inconsistent. Stay in OWL 2 EL or use pure Datalog where you can.
3. **Stale data.** KGs go out of date fast. Either re-ingest from source
   on a schedule, or query the source live and cache.
4. **Quality vs coverage tradeoff.** LLM-extracted triples have broad
   coverage but 30-40% error rates. Always layer a validation step
   (SHACL constraints, manual spot checks, embedding-based outlier
   detection).

## 9. Mini demonstration (RDFLib, ~20 lines)

```python
from rdflib import Graph, Namespace

EX = Namespace("http://example.org/")
g = Graph()
g.bind("ex", EX)
g.add((EX.Charminar, EX.locatedIn, EX.Hyderabad))
g.add((EX.Hyderabad, EX.locatedIn, EX.Telangana))
g.add((EX.Telangana, EX.locatedIn, EX.India))

# transitive closure via SPARQL property paths (the '+' after locatedIn)
q = """
SELECT ?place WHERE {
  ex:Charminar ex:locatedIn+ ?place .
}
"""
for row in g.query(q, initNs={"ex": EX}):
    print(row.place)
# -> Hyderabad, Telangana, India
```

Even without an explicit reasoner, SPARQL property paths give transitive
inference. With OWL + HermiT you get class-hierarchy and
relation-property reasoning for free.
