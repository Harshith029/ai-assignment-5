from dataclasses import dataclass, field
import json


@dataclass
class Place:
    name: str
    city: str
    category: str
    rating: float
    seasons: list[str]
    hours: float
    cost: float
    tags: list[str] = field(default_factory=list)


@dataclass
class Food:
    name: str
    city: str
    cuisine: str
    meal: str
    diets: list[str]
    cost: float
    rating: float


@dataclass
class Wine:
    name: str
    style: str
    cuisines: list[str]


@dataclass
class Hotel:
    name: str
    city: str
    tier: str
    nightly_cost: float
    rating: float


@dataclass
class Case:
    case_id: int
    city: str
    days: int
    budget: float
    diets: list[str]
    interests: list[str]
    season: str
    highlights: list[str]


@dataclass
class UserProfile:
    name: str
    daily_budget: float
    diets: list[str]
    interests: list[str]
    season: str
    days: int


class KnowledgeBase:
    def __init__(self):
        self.places = []
        self.foods = []
        self.wines = []
        self.hotels = []
        self.triples = []

    def add_place(self, place):
        self.places.append(place)
        self.triples.append((place.name, "locatedIn", place.city))
        self.triples.append((place.name, "hasCategory", place.category))

    def add_food(self, food):
        self.foods.append(food)
        self.triples.append((food.name, "servedIn", food.city))
        self.triples.append((food.name, "hasCuisine", food.cuisine))
        for diet in food.diets:
            self.triples.append((food.name, "suitableFor", diet))

    def add_wine(self, wine):
        self.wines.append(wine)
        for cuisine in wine.cuisines:
            self.triples.append((wine.name, "pairsWith", cuisine))

    def add_hotel(self, hotel):
        self.hotels.append(hotel)
        self.triples.append((hotel.name, "locatedIn", hotel.city))
        self.triples.append((hotel.name, "hasTier", hotel.tier))


class CaseBase:
    def __init__(self):
        self.cases = []

    def add(self, case):
        self.cases.append(case)

    def similarity(self, city, profile, case):
        destination = 1.0 if city.lower() == case.city.lower() else 0.0
        budget = max(0.0, 1 - abs(profile.daily_budget * profile.days - case.budget)
                     / max(profile.daily_budget * profile.days, 1))
        diet = overlap(profile.diets, case.diets)
        interests = overlap(profile.interests, case.interests)
        return 0.30 * destination + 0.25 * budget + 0.20 * diet + 0.25 * interests

    def best_match(self, city, profile):
        if not self.cases:
            return None, 0.0
        ranked = [
            (case, self.similarity(city, profile, case))
            for case in self.cases
        ]
        return max(ranked, key=lambda item: item[1])


def overlap(left, right):
    if not left:
        return 1.0
    return len(set(left) & set(right)) / len(set(left))


class InferenceEngine:
    def __init__(self, kb):
        self.kb = kb

    def places_for(self, city, season, interests):
        items = [
            place for place in self.kb.places
            if place.city == city and season in place.seasons
        ]
        if interests:
            items = [
                place for place in items
                if place.category in interests or set(place.tags) & set(interests)
            ]
        return sorted(items, key=lambda place: place.rating, reverse=True)

    def hotel_for(self, city, max_nightly):
        options = [
            hotel for hotel in self.kb.hotels
            if hotel.city == city and hotel.nightly_cost <= max_nightly
        ]
        return max(options, key=lambda hotel: hotel.rating, default=None)

    def meals_for(self, city, diets):
        foods = [food for food in self.kb.foods if food.city == city]
        if diets:
            foods = [food for food in foods if set(food.diets) & set(diets)]

        result = {"breakfast": [], "lunch": [], "dinner": []}
        for food in sorted(foods, key=lambda item: item.rating, reverse=True):
            if food.meal in result:
                result[food.meal].append(food)
        return result

    def wine_for(self, cuisine):
        return [
            wine for wine in self.kb.wines
            if cuisine.lower() in [item.lower() for item in wine.cuisines]
        ]


class TravelPlanner:
    def __init__(self, kb, case_base):
        self.kb = kb
        self.case_base = case_base
        self.engine = InferenceEngine(kb)

    def plan(self, city, profile):
        places = self.engine.places_for(city, profile.season, profile.interests)
        if not places:
            places = self.engine.places_for(city, profile.season, [])

        hotel = self.engine.hotel_for(city, profile.daily_budget * 0.40)
        meals = self.engine.meals_for(city, profile.diets)
        case, similarity = self.case_base.best_match(city, profile)

        daily = []
        per_day = max(1, len(places) // profile.days)
        for index in range(profile.days):
            day_places = places[index * per_day:(index + 1) * per_day]
            breakfast = meals["breakfast"][:1]
            lunch = meals["lunch"][:1]
            dinner = meals["dinner"][:1]
            wine = self.engine.wine_for(dinner[0].cuisine)[:1] if dinner else []
            cost = (
                (hotel.nightly_cost if hotel else 0)
                + sum(place.cost for place in day_places)
                + sum(food.cost for food in breakfast + lunch + dinner)
            )
            daily.append({
                "day": index + 1,
                "places": [place.name for place in day_places],
                "meals": {
                    "breakfast": [food.name for food in breakfast],
                    "lunch": [food.name for food in lunch],
                    "dinner": [food.name for food in dinner],
                    "wine_pairing": [item.name for item in wine],
                },
                "estimated_cost": round(cost, 2),
            })

        result = {
            "traveller": profile.name,
            "destination": city,
            "hotel": hotel.name if hotel else "No hotel within budget",
            "hotel_tier": hotel.tier if hotel else "-",
            "itinerary": daily,
            "total_estimated_cost": round(sum(day["estimated_cost"] for day in daily), 2),
        }
        if case and similarity >= 0.70:
            result["cbr_insight"] = {
                "retrieved_case_id": case.case_id,
                "similarity": round(similarity, 2),
                "reused_highlights": adapt_highlights(case.highlights, self.kb, profile.diets),
            }
        return result


def adapt_highlights(highlights, kb, diets):
    adapted = []
    for item in highlights:
        food = next((food for food in kb.foods if food.name == item), None)
        if food is None or not diets or set(food.diets) & set(diets):
            adapted.append(item)
            continue

        substitute = next(
            (
                other.name for other in kb.foods
                if other.city == food.city and other.meal == food.meal
                and set(other.diets) & set(diets)
            ),
            item,
        )
        adapted.append(f"{substitute} (adapted)")
    return adapted


def build_kb():
    kb = KnowledgeBase()

    kb.add_place(Place("Eiffel Tower", "Paris", "landmark", 4.8,
                       ["spring", "summer", "autumn"], 3, 26, ["romantic"]))
    kb.add_place(Place("Louvre Museum", "Paris", "museum", 4.9,
                       ["spring", "autumn", "winter"], 4, 17, ["art", "history"]))
    kb.add_place(Place("Montmartre", "Paris", "landmark", 4.5,
                       ["spring", "summer", "autumn"], 2, 0, ["art"]))
    kb.add_place(Place("Colosseum", "Rome", "landmark", 4.9,
                       ["spring", "autumn"], 2, 16, ["history", "ancient"]))
    kb.add_place(Place("Pantheon", "Rome", "landmark", 4.8,
                       ["spring", "summer", "autumn"], 1, 0, ["history", "ancient"]))
    kb.add_place(Place("Vatican Museums", "Rome", "museum", 4.8,
                       ["spring", "autumn", "winter"], 4, 17, ["art", "history"]))

    kb.add_food(Food("Croissant and Coffee", "Paris", "French", "breakfast",
                     ["vegetarian"], 8, 4.4))
    kb.add_food(Food("Ratatouille", "Paris", "French", "lunch",
                     ["vegan", "vegetarian"], 20, 4.6))
    kb.add_food(Food("Vegetable Gratin", "Paris", "French", "dinner",
                     ["vegetarian"], 25, 4.4))
    kb.add_food(Food("Cornetto and Espresso", "Rome", "Italian", "breakfast",
                     ["vegetarian"], 5, 4.6))
    kb.add_food(Food("Cacio e Pepe", "Rome", "Italian", "dinner",
                     ["vegetarian"], 18, 4.8))
    kb.add_food(Food("Pasta al Pomodoro", "Rome", "Italian", "lunch",
                     ["vegan", "vegetarian"], 14, 4.6))

    kb.add_wine(Wine("Bordeaux Rouge", "red", ["French"]))
    kb.add_wine(Wine("Sancerre", "white", ["French"]))
    kb.add_wine(Wine("Chianti Classico", "red", ["Italian"]))
    kb.add_wine(Wine("Prosecco", "sparkling", ["Italian"]))

    kb.add_hotel(Hotel("Generator Paris", "Paris", "budget", 60, 4.0))
    kb.add_hotel(Hotel("Hotel Artemide", "Rome", "mid", 150, 4.4))
    kb.add_hotel(Hotel("The Yellow Hostel", "Rome", "budget", 45, 4.1))
    return kb


def build_cases():
    cases = CaseBase()
    cases.add(Case(101, "Paris", 3, 750, ["vegetarian"], ["museum", "art"],
                   "spring", ["Louvre Museum", "Eiffel Tower", "Ratatouille"]))
    cases.add(Case(102, "Rome", 2, 300, [], ["history", "ancient"],
                   "autumn", ["Colosseum", "Pantheon", "Cacio e Pepe"]))
    return cases


def demo():
    planner = TravelPlanner(build_kb(), build_cases())
    profiles = [
        ("Paris", UserProfile("Alice", 250, ["vegetarian"],
                              ["museum", "art", "landmark"], "spring", 3)),
        ("Rome", UserProfile("Bob", 150, [],
                             ["history", "ancient"], "autumn", 2)),
    ]
    for city, profile in profiles:
        print("=" * 60)
        print(f"{profile.name} - {city}")
        print("=" * 60)
        print(json.dumps(planner.plan(city, profile), indent=2))


if __name__ == "__main__":
    demo()
