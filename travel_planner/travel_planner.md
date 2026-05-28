# AI-Based Travel Planner (Part 2)

Design for a travel planner that reuses existing knowledge bases in
the domain - wine ontology, tourist places, food recommendation,
personalised tour plans, cost assessment. Three big building blocks:

1. **Existing public knowledge bases** (Wikidata, OpenStreetMap, Stanford
   Wine Ontology, FoodOn, etc.) - so we never re-encode facts that some
   community has already curated.
2. **Case-Based Reasoning (CBR)** for personalisation - we keep a memory
   of past trips and adapt the closest one to the new user, instead of
   building each itinerary from scratch.
3. **A constrained-optimisation step** for the actual cost-assessment
   and day-by-day scheduling.

The CBR part is straight out of Main, Dillon & Shiu, "A Tutorial on
Case-Based Reasoning", which was shared along with the assignment.

## 1. Why this problem suits CBR

The CBR tutorial gives a checklist of when CBR is a good fit. Travel
planning passes every one of them:

| CBR test | Travel planning |
|---|---|
| Does the domain have an underlying model? | Yes - geography, transport, cuisine etc. are stable enough to reason about. |
| Are there exceptions and novel cases? | Constantly - every traveller has a different mix of diet, budget, pace, interests. |
| Do cases recur? | Yes - similar destinations, similar group sizes, similar budgets show up again and again. |
| Is there significant benefit to adapting past solutions? | A lot. Building a 7-day Kerala itinerary from scratch (sights, lodging, food, transport, timing) is much more work than tweaking a known good 7-day Kerala plan. |
| Are previous cases obtainable? | Yes - tour operators, blog itineraries, the system's own previous outputs. |

CBR also gives us things a pure rule-based or pure-LLM system would
struggle with: graceful degradation when data is missing, the ability
to explain a recommendation by pointing to a previous successful trip,
and continuous learning as new trips are tried and rated.

## 2. Knowledge bases the planner reuses

The planner does not maintain its own facts. It pulls from:

| Domain | Knowledge base | Why |
|---|---|---|
| Tourist places, sights, monuments | **Wikidata** (SPARQL), **DBpedia**, **OpenStreetMap** (Overpass API) | Free, structured, multilingual, near-global coverage |
| Wine | **Stanford Wine Ontology** (OWL) - the canonical wine/food-pairing example | Demonstrates real ontological reasoning over food-wine pairings |
| Food / cuisine | **FoodOn** (food ontology), **Wikidata cuisine classes**, **TheMealDB** API | FoodOn has 30k+ classified food items with regional cuisine links |
| Hotels / lodging | **Booking.com API**, **Amadeus Hotel Search**, **Airbnb data** | Real-time price + availability |
| Flights / transport | **Amadeus Flight Offers**, **Skyscanner**, **Rome2Rio** | Multi-modal route + price |
| Weather | **Open-Meteo**, **OpenWeatherMap** | Trip-date suitability check |
| Reviews | **Google Places API**, **TripAdvisor** | Filter low-quality places |
| User profile | Local DB | Diet, budget, pace, interests, past trips |

Reusing all of this means the system inherits decades of curated data
and stays fresh without manual maintenance.

## 3. System architecture

```
+--------------------------------------------------------------+
|  USER (chat or form)                                         |
|  "5-day Kerala trip, vegetarian, INR 40k budget, slow pace"  |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  1. INTENT + CONSTRAINT EXTRACTION (LLM)                     |
|     -> {destination, days, diet, budget, pace, interests}    |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  2. CASE-BASED RETRIEVAL                                     |
|  - look up similar past trips in the case base               |
|  - similarity = weighted distance over destination, days,    |
|    diet, budget, pace, interest vector                       |
|  - return top-k candidate cases                              |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  3. KB RETRIEVAL LAYER  (parallel async calls)               |
|  - Wikidata SPARQL: top sights in Kerala by type             |
|  - OpenStreetMap Overpass: beaches, temples within radius    |
|  - FoodOn / Wikidata: regional vegetarian dishes             |
|  - Amadeus: flights to COK                                   |
|  - Booking.com: hotels under budget                          |
|  - Open-Meteo: weather forecast for the dates                |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  4. CBR ADAPTATION                                           |
|  - take the retrieved case as a starting itinerary           |
|  - swap items that no longer fit (closed venues, diet, etc.) |
|  - re-rank against the new user's interests                  |
|  - patch in fresh data from the KB layer                     |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  5. ITINERARY OPTIMISER                                      |
|  - cluster sights by location (k-means on lat/lon)           |
|  - small TSP per day (OR-Tools)                              |
|  - assign meals from local cuisine pool                      |
|  - assign lodging once per cluster                           |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  6. COST ASSESSMENT                                          |
|     total = flights + hotels*nights + meals*days             |
|           + sum(entry_fees) + intercity_transport            |
|     keep total <= budget; suggest tradeoffs if over          |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  7. PRESENTATION (LLM writes the narrative; JSON for app)    |
+--------------------------------------------------------------+
                            |
                            v
+--------------------------------------------------------------+
|  8. CASE RETENTION                                           |
|  - after the trip, collect rating + actual cost              |
|  - if successful, add the adapted plan back to the case base |
+--------------------------------------------------------------+
```

The CBR loop above is essentially the four-step "retrieve, reuse,
revise, retain" cycle from the CBR literature (Aamodt & Plaza 1994,
also covered in the Main/Dillon/Shiu tutorial).

## 4. Case representation

A case in the case base is an attribute-value pair of (problem, solution),
following the standard CBR representation in the tutorial:

**Problem features**
- destination (string + Wikidata QID)
- duration in days
- group size + composition (adults/kids)
- diet (veg / non-veg / vegan / gluten-free / ...)
- budget (numeric, currency-normalised)
- pace (slow / moderate / packed)
- interest vector (heritage, beach, food, trekking, nightlife, ...)
- travel month (for weather seasonality)

**Solution features**
- ordered list of (day, items)
- items: sights, meals, lodgings, transport legs, with entries
- actual total cost
- post-trip rating (when known)

We follow the CBR tutorial's advice to also store the level of success
of each case - cases with low ratings are still kept (you want to avoid
repeating mistakes) but they're flagged.

## 5. Retrieval

Standard k-nearest-neighbour retrieval with a weighted distance:

```
sim(case_a, case_b) = w1*sim(destination)
                    + w2*sim(duration)
                    + w3*sim(diet)
                    + w4*sim(budget)
                    + w5*sim(pace)
                    + w6*cosine(interest_vec_a, interest_vec_b)
```

- Destination similarity: hierarchical - same city > same state > same
  country > same continent. We use the Wikidata `P131` (located in
  administrative entity) chain to compute it.
- Diet similarity: a small lookup table (veg matches vegan partially,
  veg does not match non-veg, etc.).
- Budget similarity: 1 - |b_a - b_b| / max(b_a, b_b).
- Interest similarity: cosine over an interest vector (~20 dimensions).

The weights are tuned offline against held-out trip ratings.

For indexing we use a discrimination network on the categorical fields
(destination region, diet) and brute-force nearest neighbour within
each bucket. For 10k+ cases we'd add an embedding-based index (e.g.
FAISS over a sentence-encoder summary of each case).

## 6. Adaptation

Adaptation is where the retrieved case is transformed into something
that fits the new query. We use a few common adaptation strategies
from the tutorial:

- **Substitution** - swap items that don't fit the new constraints.
  Example: the retrieved case had a non-veg fish-based meal; we
  substitute with a comparable vegetarian dish from the same region
  using FoodOn / Wikidata.
- **Parameter adjustment** - scale durations and budgets proportionally
  when the new query has a different number of days or party size.
- **Structural transformation** - if the retrieved case is for 5 days
  and the new query is 7, we expand by cloning the "buffer" day pattern
  or by inserting an extra location cluster.
- **Re-ranking** - sights and meals are re-scored against the new
  user's interest vector and the top-k retained per day.

If adaptation fails (e.g. nothing in the case base is close enough),
the system falls back to building from scratch via the KB layer + the
optimiser, then stores the new plan as a fresh case.

## 7. Ontology reuse - concrete examples

### a) Tourist sights from Wikidata
```sparql
SELECT ?place ?placeLabel ?lat ?lon ?image WHERE {
  ?place wdt:P131 wd:Q1186 ;             # located in Kerala
         wdt:P31/wdt:P279* wd:Q570116 .  # instance of tourist attraction
  ?place p:P625 ?coord .
  ?coord psv:P625 ?coordNode .
  ?coordNode wikibase:geoLatitude ?lat ;
             wikibase:geoLongitude ?lon .
  OPTIONAL { ?place wdt:P18 ?image }
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }
}
LIMIT 50
```

### b) Wine pairing via the Stanford Wine Ontology
Load the ontology with RDFLib + OWLready2, then query:
```sparql
PREFIX wine: <http://www.w3.org/TR/owl-guide/wine.rdf#>
PREFIX food: <http://www.w3.org/TR/owl-guide/food.rdf#>

SELECT ?wine WHERE {
  ?wine a wine:Wine ;
        wine:hasFlavor wine:Strong ;
        wine:hasBody   wine:Full .
  food:SpicyRedMeat food:hasDrink ?wine .
}
```
This is the textbook example of reusing a published ontology for
inference instead of re-encoding facts.

### c) Nearby attractions via OpenStreetMap Overpass
```
[out:json];
( node["tourism"="attraction"](around:25000, 9.9312, 76.2673);
  node["tourism"="viewpoint"](around:25000, 9.9312, 76.2673); );
out center;
```

## 8. Personalisation strategies

| Signal | Source | How it's used |
|---|---|---|
| Past trips | local DB / case base | Direct CBR retrieval; also embedded for "more like this" suggestions |
| Stated interests | form / chat | Weighted scoring against Wikidata `instance of` classes |
| Diet | explicit | Hard filter on cuisine + restaurant tags |
| Pace | slow / moderate / packed | Maps to a max sights/day cap (3 / 5 / 8) |
| Budget | numeric | Constrains hotel tier + flight class + optional activities |
| Reviews | Google Places | Drop anything < 4.0 with > 50 reviews |

## 9. Cost assessment module

This is the constrained-budget allocator:

```
minimise    regret(itinerary) = sum of (preference_score_lost)
subject to  sum(costs) <= user_budget
            >= 1 hotel per location cluster
            >= 2 meals per day
            travel_time(day) <= max_hours[pace]
```

For trips under ~10 days this is small enough to solve directly with
**OR-Tools CP-SAT**. Larger trips degrade gracefully to a greedy
heuristic.

## 10. Tech stack

| Layer | Choice | Reason |
|---|---|---|
| Backend | FastAPI (Python) | Async - useful for parallel KB calls |
| LLM | Claude / GPT API | Intent extraction + final narrative |
| Ontology engine | RDFLib + OWLready2 | Load Stanford wine ontology, run HermiT |
| Case base | SQLite (small) -> Postgres + pgvector (larger) | Fast nearest-neighbour over a precomputed case embedding |
| Graph store (optional) | Neo4j | If we want to persist a per-user KG of preferences and friends |
| Caching | Redis (24h TTL on SPARQL results) | Wikidata is slow; same destination = same data |
| Optimiser | Google OR-Tools | TSP + CP-SAT budgeting |
| Frontend | React + Mapbox GL | Show itinerary on a map |

## 11. Failure modes and mitigations

1. **SPARQL endpoints rate-limit.** Mitigate with aggressive caching and
   a fallback to a local Wikidata dump (HDT format, ~100 GB).
2. **Long-tail destinations have sparse Wikidata coverage.** Fall back
   to OSM + LLM-generated descriptions, flagged as lower-confidence.
3. **Stale prices.** Hotel and flight prices change minute to minute.
   Only bind a quote at checkout via the partner API.
4. **Ontology mismatch.** The Stanford wine ontology uses URIs that
   don't match Wikidata's wine entities. We need an alignment layer
   (LogMap, AML) to map between them.
5. **LLM hallucination.** Keep the LLM in the *extraction* and
   *narrative* roles only. Never let it invent places, prices, or
   restaurant names - those come from the KBs.
6. **CBR case-base poisoning.** If a bad trip ends up rated high (e.g.
   the user rated the experience, not the plan), we slowly corrupt the
   case base. Mitigation: separate "plan quality" rating from
   "experience quality" rating; only the former feeds back into CBR.

## 12. Why this beats a pure-LLM travel planner

A naked LLM hallucinates flight times, makes up restaurants, and gets
prices wrong. This architecture pins every factual claim to either a
real KB or a live API, keeping the LLM in a stylistic role only. CBR
adds the bit a pure LLM doesn't have - explicit memory of what
actually worked for similar travellers in the past.

## 13. MVP scope (what I'd build first)

Week-1 MVP, single city:
1. Wikidata SPARQL for sights + Overpass for restaurants.
2. Static hotel data (nightly Booking.com scrape, not live).
3. Hard-coded flight prices.
4. Greedy day-clustering (skip OR-Tools).
5. Tiny case base seeded with a handful of curated itineraries.
6. Markdown output, no map.

Add the real-time price APIs, the wine ontology reasoning, the full
CBR adaptation engine, and the constraint optimiser only after the
basic loop reliably produces sensible itineraries.

## 14. References

- Main, J., Dillon, T., & Shiu, S. (2001). *A Tutorial on Case-Based
  Reasoning*. In Sankar K. Pal, T. Dillon & D. Yeung (eds.), Soft
  Computing in Case Based Reasoning. Springer-Verlag, pp. 1-28.
  (The CBR design here follows the workflow and case-representation
  guidance in this tutorial.)
- Aamodt, A., & Plaza, E. (1994). Case-Based Reasoning: Foundational
  Issues, Methodological Variations, and System Approaches. AI
  Communications, 7(1), 39-59.
