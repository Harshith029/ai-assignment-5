# AI-Based Travel Planner

## Objective

Design a travel planner that reuses existing knowledge-base ideas from tourism:
tourist places, food recommendations, wine pairing, personalized tour plans, and
cost assessment.

This implementation is a small offline prototype. It does not call live APIs,
but it models how a larger system would reuse knowledge bases.

## Knowledge Sources Reused

| Domain | Knowledge-base idea used in this demo |
|---|---|
| Tourist places | Places have city, category, season, rating, visit time, and cost |
| Food recommendation | Foods are tagged by cuisine, meal type, diet, city, and rating |
| Wine ontology | Wines contain cuisine-pairing knowledge such as French or Italian |
| Personalized plans | A case base stores previous trips and retrieves similar cases |
| Cost assessment | Daily hotel, attraction, and food costs are added into a total |

## System Architecture

```text
User Profile
  name, budget, diet, interests, season, days
        |
        v
Case-Based Reasoning
  retrieve similar previous trip
  reuse/adapt highlights
        |
        v
Inference Engine
  filter seasonal places
  rank by interests and rating
  select hotel within budget
  choose diet-safe meals
  infer wine pairing from cuisine
        |
        v
Cost Assessment
  hotel + attraction entry + meals
        |
        v
JSON Itinerary
```

## Important Classes

| Class | Role |
|---|---|
| `Place` | Tourist attraction data |
| `Food` | Meal recommendation data |
| `Wine` | Cuisine-to-wine pairing data |
| `Hotel` | Accommodation data |
| `Case` | Past trip for case-based reasoning |
| `UserProfile` | User preferences and constraints |
| `KnowledgeBase` | Stores entities and simple triples |
| `CaseBase` | Computes similarity with previous trips |
| `InferenceEngine` | Applies recommendation rules |
| `TravelPlanner` | Orchestrates the final itinerary |

## Case-Based Reasoning

The planner follows the standard CBR cycle:

```text
Retrieve -> Reuse -> Revise -> Retain
```

In this prototype:

- Retrieve: find the most similar previous case.
- Reuse: copy useful highlights from that case.
- Revise: adapt food highlights if the user's diet is different.
- Retain: not stored permanently here, but the design supports adding new cases
  to the `CaseBase`.

The similarity score combines destination, budget, diet, and interests:

```text
0.30 * destination
+ 0.25 * budget
+ 0.20 * diet
+ 0.25 * interests
```

## Inference Rules

### Place Recommendation

```text
IF place.city == requested_city
AND requested_season in place.seasons
AND place.category or tags match user interests
THEN recommend the place
```

### Hotel Selection

```text
hotel_budget = daily_budget * 0.40
choose the highest-rated hotel within hotel_budget
```

### Food Recommendation

```text
IF food.city == requested_city
AND food.diets overlaps user.diets
THEN food is suitable
```

### Wine Pairing

```text
IF dinner.cuisine in wine.cuisines
THEN pair that wine with dinner
```

## Cost Assessment

For each day:

```text
Daily Cost = Hotel Cost + Attraction Entry Costs + Meal Costs
```

The total trip cost is the sum of all daily costs.

## Run

```bash
python travel_planner.py
```

The demo prints JSON itineraries for:

- Alice visiting Paris as a vegetarian traveler interested in museums and art.
- Bob visiting Rome with history and ancient-site interests.

## Sample Output Shape

```json
{
  "traveller": "Alice",
  "destination": "Paris",
  "hotel": "Generator Paris",
  "hotel_tier": "budget",
  "itinerary": [
    {
      "day": 1,
      "places": ["Louvre Museum"],
      "meals": {
        "breakfast": ["Croissant and Coffee"],
        "lunch": ["Ratatouille"],
        "dinner": ["Vegetable Gratin"],
        "wine_pairing": ["Bordeaux Rouge"]
      },
      "estimated_cost": 130
    }
  ],
  "total_estimated_cost": 382,
  "cbr_insight": {
    "retrieved_case_id": 101,
    "similarity": 0.92,
    "reused_highlights": ["Louvre Museum", "Eiffel Tower", "Ratatouille"]
  }
}
```

## Possible Extensions

- Replace local tourist data with Wikidata or OpenStreetMap.
- Replace local food data with a food ontology or restaurant API.
- Add live hotel pricing from travel APIs.
- Store retained cases in a database.
- Add transport cost between places.
