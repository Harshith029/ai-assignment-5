# Travel Planner Test Cases

## Test Case 1 - Vegetarian Paris Trip

Input profile:

```python
UserProfile(
    name="Alice",
    daily_budget=250,
    diets=["vegetarian"],
    interests=["museum", "art", "landmark"],
    season="spring",
    days=3,
)
```

Expected behavior:

- destination is Paris,
- hotel is selected within 40% daily hotel budget,
- recommended meals are vegetarian,
- wine pairing is selected from French cuisine,
- CBR retrieves the Paris vegetarian case.

## Test Case 2 - Rome History Trip

Input profile:

```python
UserProfile(
    name="Bob",
    daily_budget=150,
    diets=[],
    interests=["history", "ancient"],
    season="autumn",
    days=2,
)
```

Expected behavior:

- selected places include Rome history/ancient locations,
- hotel is budget-feasible,
- Italian dinner receives an Italian wine pairing,
- CBR retrieves the Rome history case.

## Test Case 3 - Diet Adaptation

If a retrieved case includes food that does not satisfy the user's diet, the
planner replaces it with a compatible food from the same city and meal type.
