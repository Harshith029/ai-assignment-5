# Bayesian Networks (Part 4)

Explores tools for modelling, problem representation and inference using
Bayesian Networks, then picks an example to implement. The implementation
is in `bayes_alarm.py` (pgmpy + the classic burglar/alarm network). The
rest of this document is the tool survey.

The survey below draws on Canonaco et al., "A guide to bayesian networks
software for structure and parameter learning" (Frontiers in Systems
Biology, 2025), which was shared with the assignment material, plus
hands-on use of pgmpy.

## 1. What a Bayesian Network is

A Bayesian Network (BN) is a directed acyclic graph (DAG) where:
- nodes are random variables,
- edges encode direct probabilistic dependence,
- each node carries a conditional probability distribution (CPD) given
  its parents.

The whole joint distribution factorises along the graph:

```
P(X1, X2, ..., Xn) = Π P(Xi | Parents(Xi))
```

That factorisation is the entire point. Instead of storing the joint
(2^n - 1 numbers for n binary variables), you only need one CPD per
node. For the small alarm network in this assignment that means 10
parameters vs 31 - and the gap grows fast as n increases.

Two warnings worth keeping in mind (both stressed in the Canonaco paper):
edges in a BN encode conditional dependence, not necessarily causation;
and a "causal" BN only makes sense under extra assumptions (causal
sufficiency, faithfulness, no hidden confounders).

## 2. The three workflows

| Workflow | Question | How |
|---|---|---|
| Modelling | how are variables related? | hand design from expert knowledge, OR structure learning (PC, hill-climbing, MMHC, NOTEARS) |
| Inference | given evidence E, what is P(Q\|E)? | exact: variable elimination, belief propagation, junction tree; approximate: forward / rejection sampling, likelihood weighting, Gibbs, MCMC |
| Learning | estimate CPDs from data | MLE; Bayesian (Dirichlet prior, e.g. BDeu); EM for missing data |

## 3. Tools

### 3.1 Modelling / inference libraries

This list mirrors the survey by Canonaco et al. (2025) and adds tools
I've used personally.

| Tool | Language | Notes |
|---|---|---|
| **pgmpy** | Python | What I used here. Modular, covers structure learning, parameter learning, exact + approximate inference, and causal inference. Active project. |
| **bnlearn (R)** | R | The reference R package - very complete: constraint-based (PC, GS, IAMB), score-based (HC, Tabu), hybrid (MMHC, RSMAX2), parameter estimation, cross-validation, bootstrap, model averaging. Documented alongside the books "Bayesian Networks in R" and "Bayesian Networks with Examples in R". |
| **bnlearn (Python)** | Python | Separate project from the R one - simpler interface, fewer methods. |
| **pyAgrum** | Python (wraps C++ aGrUM) | Strong on dynamic BNs (time-dependent variables). GHC, LS-TL, MIIC, Chow-Liu, NB, TAN, K2. Good docs and worked examples (incl. Pearl "Book of Why" problems). |
| **Tetrad** | Java (GUI) | CMU causal-learning group. PC, FCI, PC-Max, CPC, MLE for parameter learning. Good for teaching - has a GUI and lets you draw and edit graphs by hand. |
| **causal-cmd** | Java CLI | Command-line wrapper around 30+ algorithms from the Tetrad project. Good for batch / scripted work. |
| **causal-learn** | Python | Python translation/extension of Tetrad by the same group. |
| **CDT** | Python | Causal Discovery Toolbox. Largest collection of causal-discovery algorithms; can use NumPy / scikit-learn / PyTorch / R under the hood. Best for "try lots of methods" experiments. |
| **gCastle** | Python (Huawei) | Modern causal discovery library; score-based, gradient-based, hybrid. Has a GUI. Beginner friendly. |
| **LiNGAM** | Python | Specialised for linear non-Gaussian models (Direct-LiNGAM, VAR-LiNGAM, longitudinal LiNGAM). Useful when the noise really is non-Gaussian. |
| **pcalg** | R | Constraint-based (PC, FCI, RFCI) plus hybrid and score-based algorithms. |
| **OpenMarkov** | Java (GUI) | Free, has a UI, PC + HC structure learning. |
| **pomegranate** | Python | Probability distributions, BNs, HMMs - both constraint-based and score-based structure learning. |
| **BayesFusion (GeNIe + SMILE)** | Commercial | Industry-standard GUI (GeNIe) backed by the SMILE C++ engine. Free for academic use. Wrappers for Python, R, Java, .NET, Matlab. |
| **BayesiaLab** | Commercial | Polished GUI; full suite of learning + inference algorithms. Has an ebook with tutorials. Java-only API. |
| **Bayes Server** | Commercial | Cloud or local, lots of decision-support and anomaly-detection wrappers built on top. APIs for Java, Python, R, Matlab, Spark. |

If I had to pick one starting point per use case:

- **Just doing inference on a hand-designed BN**: pgmpy (Python), or
  bnlearn if you live in R.
- **Structure learning on tabular data**: bnlearn (R) is the most complete;
  pgmpy is fine for small/medium nets.
- **Pure causal discovery** (just want the DAG, no probabilistic model):
  gCastle if you want the easiest UI; CDT if you want every algorithm
  under one roof; LiNGAM specifically if you have linear, non-Gaussian
  data.
- **Time-dependent variables**: pyAgrum or pgmpy (both partially cover
  dynamic BNs).
- **GUI / teaching**: GeNIe or BayesiaLab.

### 3.2 Inference algorithms - which to use when

| Algorithm | Type | Good for |
|---|---|---|
| Variable Elimination | exact | small/medium networks, single query |
| Junction Tree (Lauritzen-Spiegelhalter) | exact | repeated queries on the same network - amortises the cost |
| Belief Propagation | exact on polytrees, approximate (loopy BP) otherwise | polytree structure |
| Forward / Rejection sampling | approximate | easy to implement; collapses when the evidence is rare (you reject most samples) |
| Likelihood Weighting | approximate | better than rejection when evidence is rare |
| Gibbs / MCMC | approximate | very large networks where exact inference blows up |

### 3.3 Structure-learning approaches

| Approach | Algorithms | Where to find them |
|---|---|---|
| Constraint-based | PC, PC-Stable, FCI, RFCI | pgmpy, causal-learn, pcalg, bnlearn (R), Tetrad |
| Score-based | Hill-Climbing, Tabu Search, Greedy Equivalence Search | bnlearn (R), pgmpy, pyAgrum |
| Hybrid | MMHC, HPC, RSMAX2 | bnlearn (R), pyAgrum |
| Bayesian (sampling over structures) | Order-MCMC | BiDAG (R) |
| Neural / continuous-optimization | NOTEARS, DAG-GNN, GraN-DAG | gCastle, CausalNex, CDT |
| Time-series | LiNGAM family, dynamic BNs | LiNGAM, pyAgrum, pgmpy |

### 3.4 Extending BNs to causal inference (do-calculus)

When the BN is a true causal model you can answer interventional and
counterfactual questions, not just observational ones. Tools:

- **DoWhy** (Microsoft) - the standard Python library for causal inference,
  built around the four-step DoWhy workflow.
- **CausalNex** (QuantumBlack) - structure learning + intervention.
- **EconML** - heterogeneous treatment effects (causal ML).
- **CausalML** (Uber) - uplift modelling.

## 4. The implementation in this folder

`bayes_alarm.py` implements Pearl's canonical
**Burglary -> Alarm <- Earthquake** network, with `JohnCalls` and
`MaryCalls` as downstream effects of the alarm. Why this network?

1. It's small enough that every number can be checked by hand against
   the textbook (Russell & Norvig fig 14.2).
2. It contains the **explaining-away / collider** pattern, which is the
   most counter-intuitive thing BNs do - perfect for showing why you
   want a graphical model rather than Naive Bayes.
3. The whole pipeline (model, multiple inference methods, parameter
   learning) fits in roughly 150 lines, which makes it easy to read
   end to end.

The script:
1. Builds the network with explicit CPDs (modelling).
2. Runs Variable Elimination on five queries.
3. Runs Belief Propagation on one of them and confirms it matches VE
   (it should - the network is a polytree).
4. Runs forward sampling (50k samples) and shows the estimate converges
   to the exact answer.
5. Generates 200k synthetic samples and re-learns the CPDs from them
   using MLE; reports per-CPD max error.
6. Prints the explaining-away effect directly.

### Sample output (excerpts)

```
P(Burglary | J=T, M=T)
  Burglary(F):  0.7158
  Burglary(T):  0.2842        <- matches Russell & Norvig fig 14.2

P(Burglary=T | J=T, M=T)  ~  0.2857   (forward sampling, 50k samples)

Trained on 200000 simulated days.
  Burglary     max |P_true - P_learned| = 0.0001
  Earthquake   max |P_true - P_learned| = 0.0000
  Alarm        max |P_true - P_learned| = 0.4500   <- see note below
  JohnCalls    max |P_true - P_learned| = 0.0064
  MaryCalls    max |P_true - P_learned| = 0.0092

P(Burglary=T | Alarm=T)              = 0.3736
P(Burglary=T | Alarm=T, Earthquake=T) = 0.0033     <- explaining away
```

### Why the Alarm CPD has a high learning error

This isn't a bug, it's the data being too sparse for those rows. The
joint event "burglary AND earthquake on the same day" has probability
~0.001 * 0.002 = 2e-6, so 200,000 sampled days contain almost zero
instances of it. MLE has nothing to fit `P(Alarm | B=T, E=T)` from,
so that row of the CPD is essentially random.

The standard fix is **`BayesianEstimator`** with a Dirichlet (e.g. BDeu)
prior, which smooths rare events with a pseudo-count. With a strong
enough prior you trade some bias for much less variance on rare cells.

## 5. Running

```
pip install pgmpy
python bayes_alarm.py
```

Tested with Python 3.11 and pgmpy 1.x.

## 6. Why a BN here and not something else

| Alternative | Why a BN beats it for this problem |
|---|---|
| Naive Bayes | assumes features are independent given the class - kills the explaining-away effect |
| Logistic regression | no notion of latent variables; can't do interventional / counterfactual queries |
| Neural network | a black box; can't be queried symbolically; needs orders of magnitude more data |
| Markov Random Field | undirected - loses the causal asymmetry between Burglary and Alarm |

A BN is the right tool when you need symbolic, interpretable
probabilistic reasoning with explicit (causal) structure, and when at
least some of the CPDs come from expert knowledge rather than data.

## 7. Reference

Canonaco, F., Gaudillo, J., Astrologo, N., Stella, F., & Acerbi, E.
(2025). *A guide to bayesian networks software for structure and
parameter learning, with a focus on causal discovery tools*. Frontiers
in Systems Biology, 5, 1631901.
