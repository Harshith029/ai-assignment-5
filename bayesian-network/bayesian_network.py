RAIN = {True: 0.20, False: 0.80}

SPRINKLER = {
    True: {True: 0.01, False: 0.99},
    False: {True: 0.40, False: 0.60},
}

WET_GRASS = {
    (True, True): {True: 0.99, False: 0.01},
    (True, False): {True: 0.80, False: 0.20},
    (False, True): {True: 0.90, False: 0.10},
    (False, False): {True: 0.00, False: 1.00},
}


def joint(rain, sprinkler, wet):
    return RAIN[rain] * SPRINKLER[rain][sprinkler] * WET_GRASS[(rain, sprinkler)][wet]


def query(target, evidence):
    variables = ["rain", "sprinkler", "wet"]
    hidden = [name for name in variables if name != target and name not in evidence]
    values = {False: 0.0, True: 0.0}

    for target_value in [False, True]:
        for assignment in hidden_assignments(hidden):
            world = dict(evidence)
            world[target] = target_value
            world.update(assignment)
            values[target_value] += joint(world["rain"], world["sprinkler"], world["wet"])

    total = values[False] + values[True]
    return {key: value / total for key, value in values.items()}


def hidden_assignments(names):
    if not names:
        yield {}
        return
    first, rest = names[0], names[1:]
    for value in [False, True]:
        for assignment in hidden_assignments(rest):
            assignment[first] = value
            yield assignment


def show(label, result):
    print(label)
    print(f"  False: {result[False]:.4f}")
    print(f"  True : {result[True]:.4f}")


def main():
    print("Bayesian Network: Rain, Sprinkler, Wet Grass")
    print(f"P(Rain=True) = {RAIN[True]}")
    print(f"P(Sprinkler=True | Rain=True) = {SPRINKLER[True][True]}")
    print(f"P(Sprinkler=True | Rain=False) = {SPRINKLER[False][True]}")
    print()

    show("P(Rain | Wet=True)", query("rain", {"wet": True}))
    show("P(Sprinkler | Wet=True)", query("sprinkler", {"wet": True}))
    show(
        "P(Rain | Wet=True, Sprinkler=True)",
        query("rain", {"wet": True, "sprinkler": True}),
    )


if __name__ == "__main__":
    main()
