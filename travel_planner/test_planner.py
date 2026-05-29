import argparse
import io
import unittest

from kb import TravelKB, TR, WINE_NS
from planner import plan, render


def _args(**overrides):
    defaults = dict(
        destination="Tuscany", budget=1500.0, days=5,
        interests="Heritage,Food,WineTour",
        group="couple", diet="NonVeg", pace="moderate",
    )
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


_KB = None


def _kb():
    global _KB
    if _KB is None:
        _KB = TravelKB()
    return _KB


class TestPairingInference(unittest.TestCase):

    def test_dessert_pairs_with_sweet_wine(self):
        kb = _kb()
        pairings = kb.wines_for_dish("CremeBrulee", k=10)
        self.assertTrue(pairings, "no wines paired with CremeBrulee")
        recognised = ["Port", "IceWine", "Sauterne",
                      "Trochenbierenauslese", "Primavera"]
        joined = " ".join(pairings)
        self.assertTrue(any(tok in joined for tok in recognised),
                        f"none of {recognised} found in {pairings}")

    def test_red_meat_pairs_red_full(self):
        kb = _kb()
        from rdflib import URIRef
        pairings = kb.wines_for_dish("Bistecca", k=20)
        self.assertTrue(pairings)
        for w in pairings:
            wine_uri = URIRef(WINE_NS + w)
            colors = list(kb.graph.objects(wine_uri, WINE_NS.hasColor))
            bodies = list(kb.graph.objects(wine_uri, WINE_NS.hasBody))
            self.assertIn(WINE_NS.Red, colors,
                          f"{w} has no hasColor=Red after closure")
            self.assertIn(WINE_NS.Full, bodies,
                          f"{w} has no hasBody=Full after closure")


class TestBudget(unittest.TestCase):

    def test_total_within_budget(self):
        kb = _kb()
        for dest, budget in [("Tuscany", 1500), ("Kyoto", 2000), ("Goa", 800)]:
            r = plan(_args(destination=dest, budget=budget, days=4), kb=kb)
            self.assertLessEqual(r["total"], budget,
                                 f"{dest} plan overshot {budget}")

    def test_tight_budget_drops_expensive_activities(self):
        kb = _kb()
        loose = plan(_args(destination="Bordeaux", budget=2000, days=4,
                           interests="WineTour"), kb=kb)
        tight = plan(_args(destination="Bordeaux", budget=450, days=4,
                           interests="WineTour"), kb=kb)
        self.assertLess(tight["activity_cost"], loose["activity_cost"])
        self.assertLessEqual(tight["total"], 450)


class TestPersonalisation(unittest.TestCase):

    def test_different_interests_pick_different_activities(self):
        kb = _kb()
        heritage = plan(_args(destination="Kyoto", budget=1500, days=4,
                              interests="Heritage"), kb=kb)
        nature = plan(_args(destination="Kyoto", budget=1500, days=4,
                            interests="Nature"), kb=kb)
        h_day1_interests = {a[3] for a in heritage["daily"][0]}
        n_day1_interests = {a[3] for a in nature["daily"][0]}
        self.assertIn("Heritage", h_day1_interests,
                      "heritage user did not get a Heritage activity on day 1")
        self.assertIn("Nature", n_day1_interests,
                      "nature user did not get a Nature activity on day 1")
        self.assertNotEqual(heritage["daily"], nature["daily"])

    def test_vegetarian_filters_non_veg_dishes(self):
        kb = _kb()
        veg = plan(_args(destination="Goa", diet="Vegetarian"), kb=kb)
        nonveg = plan(_args(destination="Goa", diet="NonVeg"), kb=kb)
        veg_dishes = {d for d, _ in veg["dishes"]}
        nonveg_dishes = {d for d, _ in nonveg["dishes"]}
        self.assertNotIn("PorkVindaloo", veg_dishes)
        self.assertNotIn("PrawnBalchao", veg_dishes)
        self.assertIn("PorkVindaloo", nonveg_dishes)


class TestReasoning(unittest.TestCase):

    def test_derived_facts_present(self):
        kb = _kb()
        self.assertGreater(kb.derived_fact_count(), 0)
        pairs = sum(1 for _ in kb.graph.subject_objects(TR.pairsWith))
        suitable = sum(1 for _ in kb.graph.subject_objects(TR.suitableFor))
        self.assertGreater(pairs, 0)
        self.assertGreater(suitable, 0)

    def test_trace_records_rule_firings(self):
        kb = _kb()
        trace_blob = "\n".join(kb.trace)
        for rule in ["spicy", "light_fish", "red_meat", "dessert"]:
            self.assertIn(f"[{rule}] fired", trace_blob,
                          f"{rule} rule never appeared in trace")
        self.assertTrue(
            "owl-rl" in trace_blob.lower() or "hermit" in trace_blob.lower(),
            "no reasoner mention in trace")

    def test_swrl_rule_materialises_suitable_for(self):
        from rdflib import URIRef
        kb = TravelKB()
        TRO = "http://example.org/travel.owl#"
        kb.graph.add((URIRef(TRO + "u1"),
                      URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                      URIRef(TRO + "User")))
        kb.graph.add((URIRef(TRO + "u1"),
                      URIRef(TRO + "interestedIn"),
                      URIRef(TRO + "Heritage")))
        from kb import _fire_swrl_via_sparql
        n_before = sum(1 for _ in kb.graph.subject_objects(TR.suitableFor))
        _fire_swrl_via_sparql(kb.graph, [])
        n_after = sum(1 for _ in kb.graph.subject_objects(TR.suitableFor))
        self.assertGreater(n_after, n_before,
                           "suitableFor was not inferred for the new user")


class TestRenderAndPlaces(unittest.TestCase):

    def test_render_runs_and_mentions_pairings(self):
        kb = _kb()
        r = plan(_args(destination="Kyoto", diet="Vegetarian",
                       interests="Heritage,Food"), kb=kb)
        buf = io.StringIO()
        render(r, out=buf)
        text = buf.getvalue()
        self.assertIn("Trip plan: Kyoto", text)
        self.assertIn("Cost table", text)
        self.assertIn("Reasoning trace", text)

    def test_known_places(self):
        kb = _kb()
        self.assertEqual(
            set(kb.places()),
            {"Tuscany", "Bordeaux", "Kyoto", "Kerala", "Goa"})


if __name__ == "__main__":
    unittest.main(verbosity=2)
