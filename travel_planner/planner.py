import argparse
import sys

from kb import TravelKB


PACE_MAX_PER_DAY = {"slow": 2, "moderate": 3, "packed": 4}
MEAL_COST = {"solo": 12.0, "couple": 18.0, "family": 35.0, "group": 50.0}


def select_activities_ilp(activities, max_total_cost, max_count):
    try:
        import pulp
    except ImportError:
        return _select_activities_greedy(activities, max_total_cost, max_count)

    prob = pulp.LpProblem("itinerary", pulp.LpMaximize)
    x = [pulp.LpVariable(f"x_{i}", cat="Binary") for i in range(len(activities))]
    prob += pulp.lpSum(a[4] * x[i] for i, a in enumerate(activities))
    prob += pulp.lpSum(a[1] * x[i] for i, a in enumerate(activities)) <= max_total_cost
    prob += pulp.lpSum(x[i] for i in range(len(activities))) <= max_count
    solver = pulp.PULP_CBC_CMD(msg=False)
    status = prob.solve(solver)
    if pulp.LpStatus[status] != "Optimal":
        return _select_activities_greedy(activities, max_total_cost, max_count)
    return [activities[i] for i in range(len(activities))
            if pulp.value(x[i]) is not None and pulp.value(x[i]) > 0.5]


def _select_activities_greedy(activities, max_total_cost, max_count):
    sorted_acts = sorted(activities, key=lambda a: -a[4] / (a[1] + 1))
    picked, spent = [], 0.0
    for a in sorted_acts:
        if len(picked) >= max_count:
            break
        if spent + a[1] <= max_total_cost:
            picked.append(a)
            spent += a[1]
    return picked


def pick_hotel(accs, nights, max_total_cost):
    if not accs:
        return None
    affordable = [(n, c) for n, c in accs if c * nights <= max_total_cost]
    if not affordable:
        return min(accs, key=lambda x: x[1])
    return max(affordable, key=lambda x: x[1])


def schedule(picked, days, max_per_day):
    plan = [[] for _ in range(days)]
    ordered = sorted(picked, key=lambda a: -a[4])
    for idx, a in enumerate(ordered):
        day = idx % days
        attempts = 0
        while len(plan[day]) >= max_per_day and attempts < days:
            day = (day + 1) % days
            attempts += 1
        if len(plan[day]) < max_per_day:
            plan[day].append(a)
    return plan


def score_activity(activity, user_interests):
    return 3 if activity[3] in user_interests else 1


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="KB-driven travel planner (W3C wine ontology + "
                    "owlready2 + SPARQL).")
    p.add_argument("--destination", required=True,
                   help="One of: Tuscany Bordeaux Kyoto Kerala Goa")
    p.add_argument("--budget", type=float, required=True,
                   help="Total budget in EUR-equivalent units.")
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--interests", default="Heritage,Food",
                   help="Comma-separated. Options: Heritage Food WineTour "
                        "Beach Nature Adventure Nightlife")
    p.add_argument("--group", default="couple",
                   choices=["solo", "couple", "family", "group"])
    p.add_argument("--diet", default="NonVeg",
                   choices=["Vegetarian", "NonVeg", "Vegan", "GlutenFree"])
    p.add_argument("--pace", default="moderate",
                   choices=["slow", "moderate", "packed"])
    return p.parse_args(argv)


def plan(args, kb=None):
    kb = kb or TravelKB()

    if args.destination not in kb.places():
        raise ValueError(f"unknown destination: {args.destination}")

    interests = [i.strip() for i in args.interests.split(",") if i.strip()]
    user_name = f"{args.destination}_{args.group}_{args.diet}_{'_'.join(interests)}"
    kb.materialise_user(user_name, interests, args.diet)

    raw_acts = kb.activities_in(args.destination, interests=None)
    scored = [(n, c, d, i, score_activity((n, c, d, i), interests))
              for (n, c, d, i) in raw_acts]

    accs = kb.accommodations_in(args.destination)
    lodging_budget = 0.6 * args.budget
    hotel = pick_hotel(accs, args.days, lodging_budget)
    hotel_total = hotel[1] * args.days if hotel else 0

    meals_per_day = 2
    meal_cost = MEAL_COST[args.group] * meals_per_day * args.days

    activity_budget = max(0.0, args.budget - hotel_total - meal_cost)
    max_acts = PACE_MAX_PER_DAY[args.pace] * args.days

    picked = select_activities_ilp(scored, activity_budget, max_acts)
    daily = schedule(picked, args.days, PACE_MAX_PER_DAY[args.pace])

    dishes = kb.dishes_for(args.destination, diet=args.diet)
    wine_recs = []
    for dn, _ in dishes:
        for w in kb.wines_for_dish(dn, k=2):
            wine_recs.append((dn, w))

    total_activity_cost = sum(a[1] for a in picked)
    total = hotel_total + meal_cost + total_activity_cost

    return {
        "kb": kb,
        "args": args,
        "hotel": hotel,
        "hotel_total": hotel_total,
        "meal_cost": meal_cost,
        "activity_cost": total_activity_cost,
        "total": total,
        "picked": picked,
        "daily": daily,
        "dishes": dishes,
        "wine_recs": wine_recs,
    }


def render(report, out=None):
    out = out or sys.stdout
    a = report["args"]
    k = report["kb"]
    reasoner_name = {"owlrl": "OWL-RL", "hermit": "HermiT"}.get(
        k.reasoner_used, k.reasoner_used)

    out.write(f"\n=== Trip plan: {a.destination} ===\n")
    out.write(f"days={a.days}  budget={a.budget:.0f}  group={a.group}  "
              f"diet={a.diet}  pace={a.pace}\n")
    out.write(f"interests: {a.interests}\n")
    out.write(f"reasoner used: {reasoner_name}\n")

    out.write("\n# Reasoning trace\n")
    for line in k.trace[:18]:
        out.write(f"  {line}\n")
    if len(k.trace) > 18:
        out.write(f"  ... ({len(k.trace) - 18} more trace lines)\n")
    out.write(f"  derived facts in graph: {k.derived_fact_count()}\n")

    if report["hotel"]:
        out.write(f"\n# Lodging  {report['hotel'][0]}  "
                  f"({report['hotel'][1]:.0f}/night * {a.days} = "
                  f"{report['hotel_total']:.0f})\n")
    out.write(f"# Meals   {report['meal_cost']:.0f}  "
              f"(2/day * {a.days} days * {MEAL_COST[a.group]:.0f}/meal)\n")

    out.write("\n# Day plan\n")
    for di, day in enumerate(report["daily"], 1):
        out.write(f"  day {di}:\n")
        if not day:
            out.write("    (rest / buffer)\n")
        for name, cost, dur, interest, _ in day:
            out.write(f"    - {name:<22}  {interest:<10}  "
                      f"{dur:>4.1f}h  {cost:>6.0f}\n")

    out.write("\n# Recommended dishes  (diet filter: "
              f"{a.diet})\n")
    for dn, allowed in report["dishes"]:
        out.write(f"  - {dn:<20}  allows: {','.join(allowed)}\n")

    if report["wine_recs"]:
        out.write("\n# Wine pairings (from W3C wine ontology)\n")
        seen = set()
        for dn, w in report["wine_recs"]:
            if (dn, w) in seen:
                continue
            seen.add((dn, w))
            out.write(f"  {dn} pairs with {w}\n")

    out.write("\n# Cost table\n")
    out.write(f"  lodging   {report['hotel_total']:>8.0f}\n")
    out.write(f"  meals     {report['meal_cost']:>8.0f}\n")
    out.write(f"  activity  {report['activity_cost']:>8.0f}\n")
    out.write(f"  --------------------\n")
    out.write(f"  TOTAL     {report['total']:>8.0f}    "
              f"(budget {a.budget:.0f}, "
              f"{'within' if report['total'] <= a.budget else 'OVER'} budget)\n")


def main(argv=None):
    args = parse_args(argv)
    report = plan(args)
    render(report)


if __name__ == "__main__":
    main()
