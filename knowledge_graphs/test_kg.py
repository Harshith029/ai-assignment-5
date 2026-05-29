import os
import tempfile
import unittest

from rdflib import Graph

from kg import (
    EX, load_csv, save_turtle, run_query, reason, newly_inferred,
    export_html, tool_comparison,
)


def _snapshot(g):
    out = Graph()
    for t in g:
        out.add(t)
    return out


class TestBuild(unittest.TestCase):

    def test_triple_count_correctness(self):
        g = load_csv()
        self.assertEqual(len(g), 88)

    def test_save_turtle_produces_file(self):
        g = load_csv()
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "kg.ttl")
            save_turtle(g, path)
            self.assertTrue(os.path.exists(path))
            self.assertGreater(os.path.getsize(path), 500)


class TestQueries(unittest.TestCase):

    def test_sparql_returns_expected_results(self):
        g = load_csv()
        rows = run_query(g, "monuments_in_hyderabad")
        names = {str(r[0]).split("#")[-1] for r in rows}
        self.assertEqual(
            names,
            {"Charminar", "GolcondaFort", "RamojiFilmCity"})

    def test_property_path_finds_india_pre_reasoning(self):
        g = load_csv()
        direct = run_query(g, "monuments_directly_in_india")
        via_path = run_query(g, "monuments_in_india_via_path")
        self.assertEqual(len(direct), 0)
        self.assertEqual(len(via_path), 9)


class TestReasoning(unittest.TestCase):

    def test_inference_adds_expected_triples(self):
        g = load_csv()
        before_graph = _snapshot(g)
        before, after = reason(g)
        self.assertGreater(after, before)
        self.assertIn((EX.Charminar, EX.locatedIn, EX.India), g)
        self.assertIn((EX.Jaipur, EX.locatedIn, EX.India), g)

        inferred = newly_inferred(before_graph, g)
        self.assertIn((EX.Charminar, EX.locatedIn, EX.India), inferred)

    def test_reasoned_query_returns_direct_india_triples(self):
        g = load_csv()
        reason(g)
        rows = run_query(g, "monuments_directly_in_india")
        names = {str(r[0]).split("#")[-1] for r in rows}
        self.assertIn("Charminar", names)
        self.assertIn("TajMahal", names)
        self.assertEqual(len(names), 9)


class TestExportsAndTools(unittest.TestCase):

    def test_graph_export_produces_file(self):
        g = load_csv()
        reason(g)
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "graph.html")
            export_html(g, path)
            self.assertTrue(os.path.exists(path))
            with open(path, encoding="utf-8") as fh:
                html = fh.read()
            self.assertIn("Charminar", html)
            self.assertIn("vis-network", html)

    def test_tool_comparison_demos_run(self):
        g = load_csv()
        reason(g)
        demos = tool_comparison(g)
        tools = {d["tool"] for d in demos}
        self.assertEqual(tools, {"rdflib", "networkx", "neo4j"})
        rdflib_demo = [d for d in demos if d["tool"] == "rdflib"][0]
        self.assertIn("Charminar", rdflib_demo["result"])
        networkx_demo = [d for d in demos if d["tool"] == "networkx"][0]
        if networkx_demo.get("available", False):
            self.assertEqual(networkx_demo["path"][0], "Charminar")
            self.assertEqual(networkx_demo["path"][-1], "India")


if __name__ == "__main__":
    unittest.main(verbosity=2)
