from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination, BeliefPropagation
from pgmpy.sampling import BayesianModelSampling
from pgmpy.estimators import MaximumLikelihoodEstimator

try:
    from pgmpy.parameter_estimator import DiscreteMLE
    HAS_NEW_MLE = True
except ImportError:
    HAS_NEW_MLE = False

import numpy as np


def build_alarm_network():
    model = DiscreteBayesianNetwork([
        ("Burglary", "Alarm"),
        ("Earthquake", "Alarm"),
        ("Alarm", "JohnCalls"),
        ("Alarm", "MaryCalls"),
    ])

    cpd_b = TabularCPD("Burglary", 2,
                       [[0.999], [0.001]],
                       state_names={"Burglary": ["F", "T"]})

    cpd_e = TabularCPD("Earthquake", 2,
                       [[0.998], [0.002]],
                       state_names={"Earthquake": ["F", "T"]})

    cpd_a = TabularCPD("Alarm", 2,
                       [[0.999, 0.71, 0.06, 0.05],
                        [0.001, 0.29, 0.94, 0.95]],
                       evidence=["Burglary", "Earthquake"],
                       evidence_card=[2, 2],
                       state_names={"Alarm": ["F", "T"],
                                    "Burglary": ["F", "T"],
                                    "Earthquake": ["F", "T"]})

    cpd_j = TabularCPD("JohnCalls", 2,
                       [[0.95, 0.10], [0.05, 0.90]],
                       evidence=["Alarm"], evidence_card=[2],
                       state_names={"JohnCalls": ["F", "T"],
                                    "Alarm": ["F", "T"]})

    cpd_m = TabularCPD("MaryCalls", 2,
                       [[0.99, 0.30], [0.01, 0.70]],
                       evidence=["Alarm"], evidence_card=[2],
                       state_names={"MaryCalls": ["F", "T"],
                                    "Alarm": ["F", "T"]})

    model.add_cpds(cpd_b, cpd_e, cpd_a, cpd_j, cpd_m)
    assert model.check_model()
    return model


def exact_queries(model):
    ve = VariableElimination(model)
    out = {}
    out["P(Burglary | J=T, M=T)"] = ve.query(["Burglary"],
        evidence={"JohnCalls": "T", "MaryCalls": "T"})
    out["P(Alarm | J=T)"] = ve.query(["Alarm"],
        evidence={"JohnCalls": "T"})
    out["P(Burglary | A=T)"] = ve.query(["Burglary"],
        evidence={"Alarm": "T"})
    out["P(Burglary | A=T, E=T)"] = ve.query(["Burglary"],
        evidence={"Alarm": "T", "Earthquake": "T"})
    out["P(Burglary)"] = ve.query(["Burglary"])
    return out


def bp_query(model):
    return BeliefPropagation(model).query(["Burglary"],
        evidence={"JohnCalls": "T", "MaryCalls": "T"})


def sampling_query(model, n=20000, seed=0):
    np.random.seed(seed)
    samples = BayesianModelSampling(model).forward_sample(
        size=n, show_progress=False)
    mask = (samples["JohnCalls"] == "T") & (samples["MaryCalls"] == "T")
    kept = samples[mask]
    if len(kept) == 0:
        return None, 0
    return (kept["Burglary"] == "T").mean(), len(kept)


def learn_cpds(model, n=200000, seed=1):
    np.random.seed(seed)
    data = BayesianModelSampling(model).forward_sample(
        size=n, show_progress=False)
    learned = DiscreteBayesianNetwork(model.edges())
    if HAS_NEW_MLE:
        learned.fit(data, estimator=DiscreteMLE())
    else:
        learned.fit(data, estimator=MaximumLikelihoodEstimator(learned, data))
    return {c.variable: c for c in learned.get_cpds()}, data


def max_diff(a, b):
    av = np.array(a.values).flatten()
    bv = np.array(b.values).flatten()
    return float(np.max(np.abs(av - bv)))


def main():
    model = build_alarm_network()

    print("BN: Burglary -> Alarm <- Earthquake; Alarm -> John, Mary")
    print("params: joint=31  network=10\n")

    print("# Exact inference (Variable Elimination)")
    for name, q in exact_queries(model).items():
        print(f"\n{name}")
        print(q)

    print("\n# Belief Propagation (should match VE)")
    print(bp_query(model))

    print("\n# Forward sampling")
    p, k = sampling_query(model, n=50000)
    print(f"P(Burglary=T | J=T, M=T) ~ {p:.4f}   ({k} samples kept)")

    print("\n# Parameter learning (MLE on 200k samples)")
    learned, data = learn_cpds(model, n=200000)
    for cpd in model.get_cpds():
        print(f"  {cpd.variable:11s}  max|true-learned| = "
              f"{max_diff(cpd, learned[cpd.variable]):.4f}")
    print("  (Alarm row error is high because P(B and E) ~ 2e-6,")
    print("   so MLE has almost no data for those cells.)")

    print("\n# Explaining away")
    ve = VariableElimination(model)
    a_only = ve.query(["Burglary"], evidence={"Alarm": "T"})
    a_and_e = ve.query(["Burglary"],
                       evidence={"Alarm": "T", "Earthquake": "T"})
    print(f"P(Burglary=T | A=T)       = {round(float(a_only.values[1]), 4)}")
    print(f"P(Burglary=T | A=T, E=T)  = {round(float(a_and_e.values[1]), 4)}")
    print("Earthquake explains the alarm, so burglary drops sharply.")


if __name__ == "__main__":
    main()
