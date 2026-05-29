# AI-Based Travel Planner (Part 2)

A KB-driven travel planner. It loads the W3C wine ontology, builds a
small travel/food ontology with `owlready2`, runs local reasoning, and
generates a budgeted day-by-day itinerary with wine pairings.

The design document is `travel_planner.md` (kept as-is - it was the
Part-2 deliverable for the system architecture). This README covers
the working implementation: how to run it, what each file does, and
which parts reuse public knowledge bases.

## Files

- `kb.py` - loads `ontology/wine.rdf` + `ontology/food.rdf`, builds
  the travel ontology, runs reasoning, exposes `TravelKB` to the CLI.
- `planner.py` - argparse CLI; ILP (PuLP / CBC) over interest scores
  subject to a budget constraint; falls back to greedy if PuLP is
  missing.
- `test_planner.py` - 11 unit tests covering pairing inference, budget
  respect, personalisation, diet filtering, and reasoner-derived facts.
- `ontology/wine.rdf`, `ontology/food.rdf` - the W3C OWL Guide wine
  and food ontologies (~120 KB total, see "Reused KB vs project code"
  below for source).
- `demo_output.txt` - sample CLI runs for Tuscany and Kerala.

## Run

```
pip install owlready2 rdflib owlrl pulp
python planner.py --destination Tuscany --budget 1500 --days 5 \
    --interests Heritage,WineTour,Food --group couple --diet Vegetarian

python -m unittest test_planner -v
```

owlready2 calls `sync_reasoner()` for HermiT reasoning. The code also
uses `owlrl.DeductiveClosure(OWLRL_Semantics)` for the OWL-RL closure
used by the local tests and demo output. HermiT requires a Java runtime
on PATH.

## Reused KB vs project code

This is the most important table in the file.

| Component | Source | Role |
|---|---|---|
| Wine ontology (classes, properties, individual wines, hasBody / hasFlavor / hasColor / hasSugar axioms) | `https://www.w3.org/TR/owl-guide/wine.rdf` | **Reused** verbatim |
| Food ontology (PotableLiquid, EdibleThing, regional class hierarchy) | `https://www.w3.org/TR/owl-guide/food.rdf` | **Reused** verbatim |
| HermiT OWL reasoner | bundled with owlready2 | **Reused** |
| owlrl OWL 2 RL reasoner (pure Python) | `python-rdflib/OWL-RL` | **Reused** |
| `TouristPlace`, `Accommodation`, `Activity`, `User`, `Dish`, `Cuisine`, `Interest`, `Diet` classes | `kb.py` | Project ontology |
| `hasCuisine`, `pairsWith`, `locatedIn`, `suitableFor`, `costsApprox`, `servesDish`, `interestedIn`, `allows` properties | `kb.py` | Project ontology |
| 5 destinations, 5 cuisines, 15 dishes, 10 accommodations, 25 activities | `kb.py` populate() | Project seed data |
| Two SWRL rules (activity-suitable-for-user, cuisine-inherits-diet) | `kb.py` | Project rules |
| Four SPARQL pairing rules (spicy, light_fish, red_meat, dessert) keyed on the W3C ontology's hasBody / hasFlavor / hasColor / hasSugar values | `kb.py` | Project rules over W3C wine facts |
| Budgeted ILP (PuLP / CBC) | `planner.py` | Project planner |

So all the wine knowledge - which Bordeaux is full-bodied, which
Riesling is sweet, which Sauternes pairs with dessert - comes from the
W3C ontology. The travel side (places, activities, costs) is project
seed data. The reasoning that connects them - "dessert dishes pair
with wines that have hasSugar=Sweet, and the ontology says these
specific wines have that property" - is the contribution.

## How reasoning fires

`kb.py` runs these steps in order:

1. Parse `wine.rdf` + `food.rdf` into a single rdflib graph (the W3C
   files use entity-reference DTDs that owlready2 doesn't expand, so
   rdflib is the only sensible loader).
2. Build the travel ontology in owlready2 (classes, properties, SWRL
   `Imp` rules) and export it into the same rdflib graph.
3. Try `sync_reasoner()` (HermiT). The local reasoning path uses
   OWL-RL closure for the same class/property rules.
4. After closure, fire the SPARQL pairing rules. They match the dish
   profile (spicy / light_fish / red_meat / dessert) against the
   ontology's actual `hasBody` / `hasFlavor` / `hasColor` / `hasSugar`
   triples and assert `tr:pairsWith` between the dish and each
   matching wine.
5. Fire the SWRL rules as SPARQL UPDATE (the two `Imp` definitions
   are defined in OWL; the SPARQL is the equivalent executable rule
   path). The CLI also materialises the current user's
   interests into the graph before planning, so `suitableFor` facts are
   derived for that preference profile.

A reasoning trace is appended to `kb.trace` for every rule firing,
which the CLI prints. Example excerpt:

```
OWL-RL reasoning completed: 3131 -> 19836 triples
  SWRL rule [activity-suitableFor-user] fired (12 new triples)
  SWRL rule [cuisine-inherits-diet] fired (14 new triples)
  pairing rule [red_meat] fired: Bistecca pairsWith CotturiZinfandel
  pairing rule [light_fish] fired: Ribollita pairsWith MountadamRiesling
  pairing rule [dessert] fired: CremeBrulee pairsWith TaylorPort
```

The "19836 triples" number is the meaningful one - the closure step
materialised ~16,000 new triples, including the `hasColor=White`
assertions on individual wines that were previously only implied by
class restrictions like `WhiteWine subClassOf Restriction(hasColor
hasValue White)`. Without that closure the pairing SPARQL has nothing
to match on.

## What the tests check

- `test_dessert_pairs_with_sweet_wine` - the dessert rule returns a
  known sweet wine (Port, IceWine, Sauterne, Trochenbierenauslese,
  Primavera).
- `test_red_meat_pairs_red_full` - every wine paired with Bistecca
  has `hasColor=Red` AND `hasBody=Full` in the W3C ontology after
  closure. (Inference, not a lookup table.)
- `test_total_within_budget` - three destinations at three budgets;
  the planner's reported total never exceeds the budget.
- `test_tight_budget_drops_expensive_activities` - tightening the
  budget forces the ILP to drop StEmilionTasting (140) in Bordeaux.
- `test_different_interests_pick_different_activities` - the
  Heritage-interested user and the Nature-interested user get
  different day-1 activities in Kyoto.
- `test_vegetarian_filters_non_veg_dishes` - PorkVindaloo and
  PrawnBalchao are filtered out for vegetarians in Goa; non-veg users
  see them.
- `test_derived_facts_present` - `tr:pairsWith` and `tr:suitableFor`
  triple counts are both > 0 after `TravelKB()` is built.
- `test_trace_records_rule_firings` - all four pairing rules and the
  reasoner mention appear in the trace.
- `test_swrl_rule_materialises_suitable_for` - injecting a new User
  individual with `interestedIn Heritage` causes the SWRL-style rule
  to assert `suitableFor` triples that weren't there before.
- `test_render_runs_and_mentions_pairings` - the CLI render path
  produces a trip plan with a cost table and a reasoning trace section.
- `test_known_places` - sanity check on the populated destinations.

## Sample output (from `demo_output.txt`)

```
=== Trip plan: Tuscany ===
days=5  budget=1500  group=couple  diet=Vegetarian  pace=moderate
interests: Heritage,WineTour,Food
reasoner used: OWL-RL

# Day plan
  day 1:
    - UffiziGallery           Heritage     3.0h      25
  day 2:
    - SanGimignanoWalk        Heritage     4.0h       0
  day 3:
    - PastaWorkshop           Food         3.0h      80
  day 4:
    - ChiantiWineTour         WineTour     5.0h     120
  day 5:
    - ValDOrciaHike           Nature       6.0h      15

# Wine pairings (from W3C wine ontology)
  Ribollita pairs with MountadamRiesling
  Ribollita pairs with StonleighSauvignonBlanc
  PappaAlPomodoro pairs with MountadamRiesling

# Cost table
  lodging        450
  meals          180
  activity       240
  --------------------
  TOTAL          870    (budget 1500, within budget)
```

## Java / HermiT note

owlready2's HermiT integration needs a Java runtime on PATH. The local
test run uses OWL-RL closure as the portable reasoning path, which is
enough for the class/property inferences used in this project.

## References

- W3C OWL Guide, Wine ontology:
  `https://www.w3.org/TR/owl-guide/wine.rdf`
- W3C OWL Guide, Food ontology:
  `https://www.w3.org/TR/owl-guide/food.rdf`
- Lamy J.-B., *Owlready: Ontology-oriented programming in Python with
  automatic classification and high level constructs for biomedical
  ontologies*, Artificial Intelligence in Medicine 80, 2017, 11-28.
- Horrocks I., Patel-Schneider P. et al., *SWRL: A Semantic Web Rule
  Language Combining OWL and RuleML*, W3C Member Submission, 2004.
