# Knowledge Graphs and Tools

## What Is a Knowledge Graph?

A Knowledge Graph is a structured representation of entities and the
relationships between them. It stores knowledge as connected facts.

In triple form, a fact looks like:

```text
subject -- predicate --> object
```

Examples:

```text
Rahul -- STUDIES --> Artificial Intelligence
Professor Meera -- TEACHES --> Artificial Intelligence
Artificial Intelligence -- BELONGS_TO --> CSE Department
```

Knowledge graphs are useful because they make relationships explicit and
queryable.

## Why Knowledge Graphs Are Important

Traditional tables store rows and columns well, but they are less natural when
the main value is in connections. Knowledge graphs are useful for:

- semantic search,
- recommendation systems,
- question answering,
- fraud detection,
- healthcare knowledge bases,
- social-network analysis,
- enterprise data integration,
- retrieval augmented generation systems.

## Components of a Knowledge Graph

| Component | Meaning |
|---|---|
| Entity/node | A real-world object such as a person, course, city, or product |
| Relationship/edge | A typed link between two entities |
| Property | Extra data about a node or edge |
| Ontology/schema | Definition of allowed classes and relationships |
| Query language | Language used to retrieve facts and patterns |
| Reasoner | Optional engine that derives new facts from rules |

## Types of Graph Databases

| Type | Description | Examples |
|---|---|---|
| Property graph | Nodes and relationships have labels and properties | Neo4j, Memgraph |
| RDF triple store | Stores subject-predicate-object triples with URIs | GraphDB, Apache Jena, Stardog |
| Distributed graph database | Built for huge graph workloads | JanusGraph, Amazon Neptune |

## Tools to Build Knowledge Graphs

### Neo4j

Neo4j is a popular property graph database. It uses Cypher query language and
is beginner-friendly for modelling connected data.

### GraphDB

GraphDB is an RDF triple store. It is useful when semantic-web standards,
ontologies, RDF, OWL, and SPARQL are required.

### Apache Jena

Apache Jena is an open-source Java framework for RDF data. It includes Fuseki,
a SPARQL server.

### Protege

Protege is an ontology editor. It is used to design classes, properties,
restrictions, and OWL ontologies.

### Gephi

Gephi is a graph visualization and analysis tool. It is useful for exploring
large networks visually.

### LangChain and LlamaIndex

These tools can help extract entities and relationships from text documents and
connect them to graph or retrieval systems.

## Mini Implementation - University Knowledge Graph

### Entities

- `Student`
- `Professor`
- `Course`
- `Department`

### Relationships

- `Student STUDIES Course`
- `Professor TEACHES Course`
- `Student BELONGS_TO Department`
- `Professor BELONGS_TO Department`
- `Course BELONGS_TO Department`

### Example Graph

```text
Rahul --STUDIES--> Artificial Intelligence
Meera --TEACHES--> Artificial Intelligence
Artificial Intelligence --BELONGS_TO--> CSE Department
Rahul --BELONGS_TO--> CSE Department
```

### Cypher Creation Example

```cypher
CREATE (:Student {name: 'Rahul', id: 'S101', year: 3});
CREATE (:Professor {name: 'Meera', id: 'P10', specialization: 'AI'});
CREATE (:Course {name: 'Artificial Intelligence', code: 'CS2201'});
CREATE (:Department {name: 'CSE', building: 'Block A'});

MATCH (s:Student {id: 'S101'}), (c:Course {code: 'CS2201'})
CREATE (s)-[:STUDIES]->(c);

MATCH (p:Professor {id: 'P10'}), (c:Course {code: 'CS2201'})
CREATE (p)-[:TEACHES]->(c);

MATCH (c:Course {code: 'CS2201'}), (d:Department {name: 'CSE'})
CREATE (c)-[:BELONGS_TO]->(d);
```

### Query Example

Find all students and the courses they study:

```cypher
MATCH (s:Student)-[:STUDIES]->(c:Course)
RETURN s.name AS student, c.name AS course;
```

Find all courses taught by a professor:

```cypher
MATCH (p:Professor)-[:TEACHES]->(c:Course)
WHERE p.name = 'Meera'
RETURN c.name;
```

## RDF Equivalent

The same facts can be written as RDF triples:

```text
ex:Rahul ex:studies ex:ArtificialIntelligence .
ex:Meera ex:teaches ex:ArtificialIntelligence .
ex:ArtificialIntelligence ex:belongsTo ex:CSE .
```

SPARQL query:

```sparql
SELECT ?student ?course WHERE {
  ?student ex:studies ?course .
}
```

## Conclusion

Knowledge graphs help AI systems represent relationships in a structured way.
They are especially useful when answers require following links between facts,
not just searching text.
