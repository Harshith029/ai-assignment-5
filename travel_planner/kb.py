import os
import shutil

from owlready2 import (
    get_ontology, Thing, ObjectProperty, DataProperty,
    FunctionalProperty, Imp, sync_reasoner, default_world,
)
from rdflib import Graph, Namespace, Literal, URIRef, RDF
import owlrl


HERE = os.path.dirname(os.path.abspath(__file__))
WINE_RDF = os.path.join(HERE, "ontology", "wine.rdf")
FOOD_RDF = os.path.join(HERE, "ontology", "food.rdf")

WINE_NS = Namespace("http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#")
FOOD_NS = Namespace("http://www.w3.org/TR/2003/PR-owl-guide-20031209/food#")
TR = Namespace("http://example.org/travel#")


def build_travel_ontology():
    onto = get_ontology("http://example.org/travel.owl")

    with onto:
        class TouristPlace(Thing): pass
        class Cuisine(Thing): pass
        class Wine(Thing): pass
        class Accommodation(Thing): pass
        class Activity(Thing): pass
        class User(Thing): pass
        class Dish(Thing): pass

        class Interest(Thing): pass
        class Diet(Thing): pass

        class hasCuisine(ObjectProperty):
            domain = [TouristPlace]
            range = [Cuisine]

        class servesDish(ObjectProperty):
            domain = [Cuisine]
            range = [Dish]

        class pairsWith(ObjectProperty):
            domain = [Dish]
            range = [Wine]

        class locatedIn(ObjectProperty):
            domain = [Thing]
            range = [TouristPlace]

        class suitableFor(ObjectProperty):
            domain = [Activity]
            range = [User]

        class about(ObjectProperty):
            range = [Interest]

        class interestedIn(ObjectProperty):
            domain = [User]
            range = [Interest]

        class allows(ObjectProperty):
            range = [Diet]

        class prefers(ObjectProperty):
            domain = [User]
            range = [Diet]

        class costsApprox(DataProperty, FunctionalProperty):
            range = [float]

        class typicalDuration(DataProperty, FunctionalProperty):
            range = [float]

        rule_suitable = Imp()
        rule_suitable.set_as_rule(
            "Activity(?a), about(?a, ?i), User(?u), interestedIn(?u, ?i)"
            " -> suitableFor(?a, ?u)"
        )

        rule_cuisine_diet = Imp()
        rule_cuisine_diet.set_as_rule(
            "Cuisine(?c), servesDish(?c, ?d), allows(?d, ?diet)"
            " -> allows(?c, ?diet)"
        )

    return onto


def populate(onto):
    TouristPlace = onto.TouristPlace
    Cuisine = onto.Cuisine
    Accommodation = onto.Accommodation
    Activity = onto.Activity
    User = onto.User
    Interest = onto.Interest
    Diet = onto.Diet

    iv = {n: Interest(n) for n in
          ["Heritage", "Food", "WineTour", "Beach", "Nature", "Adventure", "Nightlife"]}

    dv = {n: Diet(n) for n in ["Vegetarian", "NonVeg", "Vegan", "GlutenFree"]}

    sample_user = User("HeritageFoodUser")
    sample_user.interestedIn = [iv["Heritage"], iv["Food"]]
    sample_user.prefers = [dv["Vegetarian"]]

    tuscany = TouristPlace("Tuscany")
    bordeaux = TouristPlace("Bordeaux")
    kyoto = TouristPlace("Kyoto")
    kerala = TouristPlace("Kerala")
    goa = TouristPlace("Goa")
    places = [tuscany, bordeaux, kyoto, kerala, goa]

    Dish = onto.Dish

    def dish(name, allowed):
        d = Dish(name)
        for a in allowed:
            d.allows.append(dv[a])
        return d

    italian = Cuisine("Italian")
    french = Cuisine("French")
    japanese = Cuisine("Japanese")
    south_indian = Cuisine("SouthIndian")
    goan = Cuisine("Goan")

    italian.servesDish = [
        dish("Bistecca", ["NonVeg"]),
        dish("Ribollita", ["Vegetarian", "Vegan"]),
        dish("PappaAlPomodoro", ["Vegetarian", "Vegan"]),
    ]
    french.servesDish = [
        dish("Confit", ["NonVeg"]),
        dish("Ratatouille", ["Vegetarian", "Vegan"]),
        dish("CremeBrulee", ["Vegetarian"]),
    ]
    japanese.servesDish = [
        dish("Sushi", ["NonVeg"]),
        dish("Tempura", ["Vegetarian"]),
        dish("Edamame", ["Vegetarian", "Vegan"]),
    ]
    south_indian.servesDish = [
        dish("Dosa", ["Vegetarian", "Vegan"]),
        dish("Sambar", ["Vegetarian", "Vegan"]),
        dish("FishMoilee", ["NonVeg"]),
    ]
    goan.servesDish = [
        dish("PorkVindaloo", ["NonVeg"]),
        dish("PrawnBalchao", ["NonVeg"]),
        dish("XacutiVegetable", ["Vegetarian"]),
    ]

    tuscany.hasCuisine = [italian]
    bordeaux.hasCuisine = [french]
    kyoto.hasCuisine = [japanese]
    kerala.hasCuisine = [south_indian]
    goa.hasCuisine = [goan]

    def acc(name, place, cost):
        h = Accommodation(name)
        h.locatedIn = [place]
        h.costsApprox = float(cost)
        return h

    accs = [
        acc("FlorenceB&B", tuscany, 90.0),
        acc("ChiantiVilla", tuscany, 220.0),
        acc("BordeauxChateau", bordeaux, 280.0),
        acc("BordeauxHostel", bordeaux, 45.0),
        acc("KyotoRyokan", kyoto, 180.0),
        acc("KyotoCapsule", kyoto, 35.0),
        acc("KochiHomestay", kerala, 40.0),
        acc("AlleppeyHouseboat", kerala, 130.0),
        acc("PanjimGuesthouse", goa, 35.0),
        acc("PalolemBeachHut", goa, 80.0),
    ]

    def activity(name, place, interest, cost, hours):
        a = Activity(name)
        a.locatedIn = [place]
        a.about.append(iv[interest])
        a.costsApprox = float(cost)
        a.typicalDuration = float(hours)
        return a

    acts = [
        activity("UffiziGallery", tuscany, "Heritage", 25, 3),
        activity("ChiantiWineTour", tuscany, "WineTour", 120, 5),
        activity("SanGimignanoWalk", tuscany, "Heritage", 0, 4),
        activity("PastaWorkshop", tuscany, "Food", 80, 3),
        activity("ValDOrciaHike", tuscany, "Nature", 15, 6),
        activity("StEmilionTasting", bordeaux, "WineTour", 140, 5),
        activity("CiteDuVin", bordeaux, "WineTour", 22, 3),
        activity("BordeauxCathedral", bordeaux, "Heritage", 0, 2),
        activity("DuneDuPilat", bordeaux, "Nature", 10, 5),
        activity("WineBarCrawl", bordeaux, "Nightlife", 60, 4),
        activity("KinkakujiTemple", kyoto, "Heritage", 5, 2),
        activity("FushimiInari", kyoto, "Heritage", 0, 3),
        activity("KaisekiDinner", kyoto, "Food", 90, 3),
        activity("ArashiyamaBamboo", kyoto, "Nature", 0, 3),
        activity("GionNightWalk", kyoto, "Nightlife", 0, 2),
        activity("HouseboatCruise", kerala, "Nature", 110, 24),
        activity("KathakaliShow", kerala, "Heritage", 8, 2),
        activity("SpicePlantation", kerala, "Food", 18, 4),
        activity("PeriyarTrek", kerala, "Adventure", 25, 6),
        activity("FortKochiWalk", kerala, "Heritage", 0, 3),
        activity("AnjunaBeach", goa, "Beach", 0, 4),
        activity("DudhsagarFalls", goa, "Nature", 30, 6),
        activity("BasilicaOldGoa", goa, "Heritage", 0, 2),
        activity("CurryCookingClass", goa, "Food", 35, 3),
        activity("BeachClub", goa, "Nightlife", 50, 5),
    ]

    return {
        "places": places,
        "cuisines": [italian, french, japanese, south_indian, goan],
        "accommodations": accs,
        "activities": acts,
        "interests": iv,
        "diets": dv,
        "users": [sample_user],
    }


def export_to_rdflib(onto):
    g = default_world.as_rdflib_graph()
    out = Graph()
    for s, p, o in g:
        out.add((s, p, o))
    return out


def load_wine_graph():
    g = Graph()
    g.parse(WINE_RDF)
    if os.path.exists(FOOD_RDF):
        g.parse(FOOD_RDF)
    g.bind("wine", WINE_NS)
    g.bind("food", FOOD_NS)
    g.bind("tr", TR)
    return g


PAIRING_RULES = {
    "spicy": (
        "PREFIX wine: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>\n"
        "SELECT ?wine WHERE {\n"
        "  ?wine wine:hasBody wine:Full ;\n"
        "        wine:hasFlavor wine:Strong .\n"
        "}"
    ),
    "light_fish": (
        "PREFIX wine: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>\n"
        "SELECT ?wine WHERE {\n"
        "  ?wine wine:hasFlavor wine:Delicate ;\n"
        "        wine:hasColor wine:White .\n"
        "}"
    ),
    "red_meat": (
        "PREFIX wine: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>\n"
        "SELECT ?wine WHERE {\n"
        "  ?wine wine:hasColor wine:Red ;\n"
        "        wine:hasBody wine:Full .\n"
        "}"
    ),
    "dessert": (
        "PREFIX wine: <http://www.w3.org/TR/2003/PR-owl-guide-20031209/wine#>\n"
        "SELECT ?wine WHERE {\n"
        "  ?wine wine:hasSugar wine:Sweet .\n"
        "}"
    ),
}

DISH_PROFILE = {
    "Bistecca": "red_meat",
    "PorkVindaloo": "spicy",
    "PrawnBalchao": "spicy",
    "FishMoilee": "spicy",
    "Sushi": "light_fish",
    "Confit": "red_meat",
    "Tempura": "light_fish",
    "CremeBrulee": "dessert",
    "Ribollita": "light_fish",
    "PappaAlPomodoro": "light_fish",
    "Ratatouille": "light_fish",
    "Edamame": "light_fish",
    "Dosa": "light_fish",
    "Sambar": "spicy",
    "XacutiVegetable": "spicy",
}


def infer_pairings(graph, trace):
    added = 0
    for dish, profile in DISH_PROFILE.items():
        dish_uri = URIRef(f"http://example.org/travel.owl#{dish}")
        for row in graph.query(PAIRING_RULES[profile]):
            wine_uri = row[0]
            graph.add((dish_uri, TR.pairsWith, wine_uri))
            added += 1
            trace.append(
                f"  pairing rule [{profile}] fired: "
                f"{dish} pairsWith {wine_uri.split('#')[-1]}"
            )
    return added


def run_reasoner(onto, graph, trace):
    if shutil.which("java") is not None:
        try:
            sync_reasoner([onto])
            trace.append("HermiT reasoning completed.")
            return "hermit"
        except Exception:
            pass

    before = len(graph)
    owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(graph)
    trace.append(f"OWL-RL reasoning completed: {before} -> {len(graph)} triples")

    _fire_swrl_via_sparql(graph, trace)
    return "owlrl"


def _fire_swrl_via_sparql(graph, trace):
    q1 = (
        "PREFIX tr:  <http://example.org/travel#>\n"
        "PREFIX trO: <http://example.org/travel.owl#>\n"
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        "INSERT { ?a tr:suitableFor ?u }\n"
        "WHERE {\n"
        "  ?a rdf:type trO:Activity .\n"
        "  ?a trO:about ?i .\n"
        "  ?u rdf:type trO:User .\n"
        "  ?u trO:interestedIn ?i .\n"
        "}"
    )
    before = len(graph)
    graph.update(q1)
    delta = len(graph) - before
    if delta:
        trace.append(f"  SWRL rule [activity-suitableFor-user] fired "
                     f"({delta} new triples)")

    q2 = (
        "PREFIX trO: <http://example.org/travel.owl#>\n"
        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"
        "INSERT { ?c trO:allows ?diet }\n"
        "WHERE {\n"
        "  ?c rdf:type trO:Cuisine .\n"
        "  ?c trO:servesDish ?d .\n"
        "  ?d trO:allows ?diet .\n"
        "}"
    )
    before = len(graph)
    graph.update(q2)
    delta = len(graph) - before
    if delta:
        trace.append(f"  SWRL rule [cuisine-inherits-diet] fired "
                     f"({delta} new triples)")


class TravelKB:
    def __init__(self):
        self.trace = []
        self.onto = build_travel_ontology()
        self.entities = populate(self.onto)

        self.graph = load_wine_graph()
        for s, p, o in export_to_rdflib(self.onto):
            self.graph.add((s, p, o))

        self.reasoner_used = run_reasoner(self.onto, self.graph, self.trace)
        infer_pairings(self.graph, self.trace)

    def places(self):
        return [p.name for p in self.entities["places"]]

    def materialise_user(self, user_name, interests, diet=None):
        def safe_name(text):
            return "".join(ch if ch.isalnum() else "_" for ch in text)

        TRO = Namespace("http://example.org/travel.owl#")
        user_uri = URIRef(TRO + safe_name(user_name))
        self.graph.add((user_uri, RDF.type, TRO.User))

        known_interests = set(self.entities["interests"])
        for interest in interests:
            if interest in known_interests:
                self.graph.add((user_uri, TRO.interestedIn,
                                URIRef(TRO + interest)))
        if diet in self.entities["diets"]:
            self.graph.add((user_uri, TRO.prefers, URIRef(TRO + diet)))

        before = sum(1 for _ in self.graph.subject_objects(TR.suitableFor))
        _fire_swrl_via_sparql(self.graph, self.trace)
        after = sum(1 for _ in self.graph.subject_objects(TR.suitableFor))
        return str(user_uri).split("#")[-1], after - before

    def activities_in(self, place_name, diet=None, interests=None):
        q = (
            "PREFIX trO: <http://example.org/travel.owl#>\n"
            "SELECT ?a ?c ?d ?i WHERE {\n"
            "  ?a rdf:type trO:Activity .\n"
            "  ?a trO:locatedIn ?p .\n"
            "  ?a trO:costsApprox ?c .\n"
            "  ?a trO:typicalDuration ?d .\n"
            "  ?a trO:about ?i .\n"
            "  FILTER (STR(?p) = ?pIRI)\n"
            "}"
        )
        place_iri = f"http://example.org/travel.owl#{place_name}"
        rows = []
        for r in self.graph.query(q, initBindings={"pIRI": Literal(place_iri)}):
            name = str(r[0]).split("#")[-1]
            cost = float(r[1])
            dur = float(r[2])
            interest = str(r[3]).split("#")[-1]
            if interests and interest not in interests:
                continue
            rows.append((name, cost, dur, interest))
        return rows

    def accommodations_in(self, place_name):
        q = (
            "PREFIX trO: <http://example.org/travel.owl#>\n"
            "SELECT ?a ?c WHERE {\n"
            "  ?a rdf:type trO:Accommodation .\n"
            "  ?a trO:locatedIn ?p .\n"
            "  ?a trO:costsApprox ?c .\n"
            "  FILTER (STR(?p) = ?pIRI)\n"
            "}"
        )
        place_iri = f"http://example.org/travel.owl#{place_name}"
        out = []
        for r in self.graph.query(q, initBindings={"pIRI": Literal(place_iri)}):
            out.append((str(r[0]).split("#")[-1], float(r[1])))
        return sorted(out, key=lambda x: x[1])

    COMPATIBLE_DIETS = {
        "NonVeg":     {"NonVeg", "Vegetarian", "Vegan", "GlutenFree"},
        "Vegetarian": {"Vegetarian", "Vegan"},
        "Vegan":      {"Vegan"},
        "GlutenFree": {"GlutenFree"},
    }

    def dishes_for(self, place_name, diet=None):
        q = (
            "PREFIX trO: <http://example.org/travel.owl#>\n"
            "SELECT DISTINCT ?d WHERE {\n"
            "  ?p trO:hasCuisine ?c .\n"
            "  ?c trO:servesDish ?d .\n"
            "  FILTER (STR(?p) = ?pIRI)\n"
            "}"
        )
        place_iri = f"http://example.org/travel.owl#{place_name}"
        allows_uri = URIRef("http://example.org/travel.owl#allows")
        compatible = self.COMPATIBLE_DIETS.get(diet) if diet else None
        dishes = []
        for r in self.graph.query(q, initBindings={"pIRI": Literal(place_iri)}):
            dish_uri = r[0]
            allowed = [str(x).split("#")[-1]
                       for x in self.graph.objects(dish_uri, allows_uri)]
            name = str(dish_uri).split("#")[-1]
            if compatible is None or set(allowed) & compatible:
                dishes.append((name, allowed))
        return dishes

    def wines_for_dish(self, dish_name, k=3):
        dish_uri = URIRef(f"http://example.org/travel.owl#{dish_name}")
        wines = []
        for o in self.graph.objects(dish_uri, TR.pairsWith):
            wines.append(str(o).split("#")[-1])
            if len(wines) >= k:
                break
        return wines

    def derived_fact_count(self):
        n = 0
        for _ in self.graph.subject_objects(TR.pairsWith):
            n += 1
        for _ in self.graph.subject_objects(TR.suitableFor):
            n += 1
        return n


if __name__ == "__main__":
    kb = TravelKB()
    print(f"reasoner used : {kb.reasoner_used}")
    print(f"graph triples : {len(kb.graph)}")
    print(f"pairsWith     : {sum(1 for _ in kb.graph.subject_objects(TR.pairsWith))}")
    print(f"places        : {kb.places()}")
    print("\nfirst 5 trace lines:")
    for line in kb.trace[:5]:
        print(" ", line)
