import csv
import os

from rdflib import Graph, Namespace, URIRef, RDF, RDFS, OWL
import owlrl


HERE = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(HERE, "data", "facts.csv")
TTL_PATH = os.path.join(HERE, "kg.ttl")
HTML_PATH = os.path.join(HERE, "graph.html")

EX = Namespace("http://example.org/india-kg#")


CLASS_HINTS = {
    "locatedIn":  ("Place",    "Place"),
    "capitalOf":  ("Place",    "Place"),
    "builtBy":    ("Monument", "Person"),
    "dynasty":    ("Person",   "Dynasty"),
}

KNOWN_MONUMENTS = {
    "Charminar", "GolcondaFort", "RamojiFilmCity", "TajMahal",
    "RedFort", "QutbMinar", "GatewayOfIndia", "HawaMahal",
    "MysorePalace",
}


def add_schema(g):
    g.add((EX.Place,    RDF.type, OWL.Class))
    g.add((EX.Monument, RDF.type, OWL.Class))
    g.add((EX.Person,   RDF.type, OWL.Class))
    g.add((EX.Dynasty,  RDF.type, OWL.Class))

    g.add((EX.locatedIn, RDF.type, OWL.TransitiveProperty))
    g.add((EX.capitalOf, RDFS.subPropertyOf, EX.locatedIn))

    g.add((EX.builtBy, RDFS.domain, EX.Monument))
    g.add((EX.builtBy, RDFS.range,  EX.Person))
    g.add((EX.dynasty, RDFS.domain, EX.Person))
    g.add((EX.dynasty, RDFS.range,  EX.Dynasty))


def load_csv(path=CSV_PATH):
    g = Graph()
    g.bind("ex", EX)
    add_schema(g)

    seen_entities = set()
    with open(path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            s = URIRef(EX + row["subject"])
            p = URIRef(EX + row["predicate"])
            o = URIRef(EX + row["object"])
            g.add((s, p, o))

            sh, oh = CLASS_HINTS.get(row["predicate"], (None, None))
            if sh:
                g.add((s, RDF.type, URIRef(EX + sh)))
            if oh:
                g.add((o, RDF.type, URIRef(EX + oh)))
            seen_entities.update([row["subject"], row["object"]])

    for m in KNOWN_MONUMENTS & seen_entities:
        g.add((URIRef(EX + m), RDF.type, EX.Monument))
    return g


def save_turtle(g, path=TTL_PATH):
    g.serialize(destination=path, format="turtle")
    return path


QUERIES = {
    "all_places": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT DISTINCT ?p WHERE { ?p a ex:Place } ORDER BY ?p"
    ),
    "monuments_in_hyderabad": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT ?m WHERE {\n"
        "  ?m a ex:Monument ;\n"
        "     ex:locatedIn ex:Hyderabad .\n"
        "} ORDER BY ?m"
    ),
    "monuments_directly_in_india": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT ?m WHERE {\n"
        "  ?m a ex:Monument ;\n"
        "     ex:locatedIn ex:India .\n"
        "} ORDER BY ?m"
    ),
    "monuments_in_india_via_path": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT ?m WHERE {\n"
        "  ?m a ex:Monument ;\n"
        "     ex:locatedIn+ ex:India .\n"
        "} ORDER BY ?m"
    ),
    "telangana_architects": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT DISTINCT ?builder ?monument WHERE {\n"
        "  ?monument ex:locatedIn ex:Telangana ;\n"
        "            ex:builtBy ?builder .\n"
        "}"
    ),
    "prolific_dynasties": (
        "PREFIX ex: <http://example.org/india-kg#>\n"
        "SELECT ?dyn (COUNT(?monument) AS ?n) WHERE {\n"
        "  ?monument ex:builtBy ?p .\n"
        "  ?p ex:dynasty ?dyn .\n"
        "}\n"
        "GROUP BY ?dyn\n"
        "HAVING (COUNT(?monument) > 1)\n"
        "ORDER BY DESC(?n)"
    ),
}


def run_query(g, name):
    return list(g.query(QUERIES[name]))


def reason(g):
    before = len(g)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
    return before, len(g)


def newly_inferred(g_before, g_after):
    before = set((s, p, o) for s, p, o in g_before)
    return [(s, p, o) for s, p, o in g_after if (s, p, o) not in before]


def _short(uri):
    return str(uri).split("#")[-1]


def rdflib_demo(g):
    rows = run_query(g, "monuments_in_hyderabad")
    return {
        "tool": "rdflib",
        "model": "RDF triples + SPARQL",
        "result": [_short(r[0]) for r in rows],
        "note": "best fit for standards-based semantic graphs",
    }


def networkx_demo(g):
    try:
        import networkx as nx
    except ImportError:
        return {
            "tool": "networkx",
            "available": False,
            "note": "install networkx for in-memory graph algorithms",
        }

    dg = nx.MultiDiGraph()
    for s, p, o in g:
        if not (isinstance(s, URIRef) and isinstance(o, URIRef)):
            continue
        if str(s).startswith(str(EX)) and str(o).startswith(str(EX)):
            dg.add_edge(_short(s), _short(o), label=_short(p))

    try:
        path = nx.shortest_path(dg, "Charminar", "India")
    except nx.NetworkXNoPath:
        path = []

    return {
        "tool": "networkx",
        "available": True,
        "model": "in-memory property-style graph",
        "nodes": dg.number_of_nodes(),
        "edges": dg.number_of_edges(),
        "path": path,
        "note": "best fit for algorithms; no native OWL/RDFS semantics",
    }


def neo4j_optional_demo(uri=None, user=None, password=None):
    cypher = (
        "MERGE (c:Monument {name: $monument})\n"
        "MERGE (p:Place {name: $place})\n"
        "MERGE (c)-[:LOCATED_IN]->(p)"
    )
    try:
        from neo4j import GraphDatabase
    except ImportError:
        return {
            "tool": "neo4j",
            "available": False,
            "ran": False,
            "cypher": cypher,
            "note": "neo4j driver not installed; block is intentionally optional",
        }

    uri = uri or os.environ.get("NEO4J_URI")
    user = user or os.environ.get("NEO4J_USER")
    password = password or os.environ.get("NEO4J_PASSWORD")
    if not (uri and user and password):
        return {
            "tool": "neo4j",
            "available": True,
            "ran": False,
            "cypher": cypher,
            "note": "driver installed; set NEO4J_URI/USER/PASSWORD to run",
        }

    try:
        with GraphDatabase.driver(uri, auth=(user, password)) as driver:
            with driver.session() as session:
                value = session.run("RETURN 1 AS ok").single()["ok"]
        return {
            "tool": "neo4j",
            "available": True,
            "ran": True,
            "result": value,
            "cypher": cypher,
            "note": "best fit for app-facing property graph workloads",
        }
    except Exception as e:
        return {
            "tool": "neo4j",
            "available": True,
            "ran": False,
            "cypher": cypher,
            "note": f"driver import worked, server check failed: {type(e).__name__}",
        }


def tool_comparison(g):
    return [rdflib_demo(g), networkx_demo(g), neo4j_optional_demo()]


def export_html(g, path=HTML_PATH):
    from pyvis.network import Network

    net = Network(height="700px", width="100%",
                  bgcolor="#ffffff", font_color="#222",
                  directed=True, notebook=False, cdn_resources="in_line")
    net.barnes_hut(spring_strength=0.02)

    color = {"Monument": "#d35400", "Place": "#2980b9",
             "Person": "#27ae60", "Dynasty": "#8e44ad"}

    for s in set(g.subjects()) | set(g.objects()):
        if not isinstance(s, URIRef):
            continue
        if str(s).startswith(str(EX)):
            label = _short(s)
            cls = None
            for t in g.objects(s, RDF.type):
                if isinstance(t, URIRef) and str(t).startswith(str(EX)):
                    cls = _short(t)
                    break
            net.add_node(label, label=label,
                         color=color.get(cls, "#7f8c8d"),
                         title=f"class: {cls or 'unknown'}")

    edge_seen = set()
    for s, p, o in g:
        if not (isinstance(s, URIRef) and isinstance(o, URIRef)):
            continue
        if not (str(s).startswith(str(EX)) and str(o).startswith(str(EX))):
            continue
        if p in (RDF.type, RDFS.subPropertyOf, RDFS.subClassOf,
                 RDFS.domain, RDFS.range):
            continue
        sn, on, pn = _short(s), _short(o), _short(p)
        key = (sn, pn, on)
        if key in edge_seen:
            continue
        edge_seen.add(key)
        net.add_edge(sn, on, label=pn, arrows="to")

    html = net.generate_html(notebook=False)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(html)
    return path


def main():
    g = load_csv()
    print(f"loaded {len(g)} triples from {os.path.basename(CSV_PATH)}")
    save_turtle(g)
    print(f"persisted to {os.path.basename(TTL_PATH)}")

    snapshot = Graph()
    for t in g:
        snapshot.add(t)

    print("\n# SPARQL queries (pre-inference)")
    for q in ("monuments_in_hyderabad", "monuments_directly_in_india",
              "monuments_in_india_via_path"):
        rows = run_query(g, q)
        print(f"\n## {q}  ({len(rows)} rows)")
        for r in rows[:8]:
            print("  ", " | ".join(str(x).split("#")[-1] for x in r))

    before, after = reason(g)
    print(f"\n# OWL 2 RL closure: {before} -> {after} triples")
    delta = newly_inferred(snapshot, g)
    interesting = [t for t in delta if t[1] == EX.locatedIn]
    print(f"  new ex:locatedIn triples: {len(interesting)}")
    for s, p, o in interesting[:6]:
        print(f"    {str(s).split('#')[-1]} locatedIn {str(o).split('#')[-1]}")

    print("\n# SPARQL queries (post-inference)")
    for q in ("monuments_directly_in_india", "telangana_architects",
              "prolific_dynasties"):
        rows = run_query(g, q)
        print(f"\n## {q}  ({len(rows)} rows)")
        for r in rows[:8]:
            print("  ", " | ".join(str(x).split("#")[-1] for x in r))

    print("\n# Tool comparison demos")
    for item in tool_comparison(g):
        print(f"\n## {item['tool']}")
        for k, v in item.items():
            if k != "tool":
                print(f"  {k}: {v}")

    html = export_html(g)
    print(f"\n# Interactive viz: {os.path.basename(html)}  "
          f"({os.path.getsize(html) // 1024} KB)")


if __name__ == "__main__":
    main()
