# Example: Lit-Review with Research Agenda

**Demonstrates**: Socratic intake (Engineering domain: topology optimization for aerospace; Method family: Bayesian optimization; Open problem: discrete design variables break GP surrogate assumptions) → Research Frame → user-confirmation handoff → lit-review produces per-paper blocks + 3-direction Research Agenda.

**Note**: This file is the canonical smoke-test fixture for `scripts/lit_review_validate.py`. Running `python3 scripts/lit_review_validate.py --input examples/lit_review_with_agenda.md --allow-md-only` must exit 0.

---

## Research Frame

- **engineering_domain**: Topology optimization for aerospace structural components
- **method_family_of_interest**: Bayesian optimization (BO) with Gaussian process surrogates
- **open_problem**: Discrete design variables (binary element inclusion/exclusion) violate GP smoothness and stationarity assumptions, causing BO to perform poorly relative to gradient-based SIMP methods on large-scale topology problems
- **baseline_approach**: SIMP (Solid Isotropic Material with Penalization) with sensitivity-based gradient descent
- **data_regime**: High-fidelity FEM evaluations (each ~10–120 seconds); budget of 200–1000 evaluations; simulation-only at present
- **scope_notes**: Focus on 2D and 3D structural compliance minimization; fixed load/boundary conditions; single-material problems
- **failure_modes**: ["GP surrogate assumes smooth continuous landscape — discrete variables create combinatorial jumps", "Acquisition function optimization becomes NP-hard over binary domains", "Surrogate model accuracy degrades rapidly with dimensionality (>200 elements)"]
- **scope_boundaries**: ["No multi-material optimization", "No fluid topology (e.g. flow channels)", "No manufacturing constraints beyond volume fraction"]
- **origin_layer**: 3
- **validation_status**: frame-converged

---

## Executive Summary

Topology optimization for aerospace structural components currently relies on gradient-based SIMP methods, which are efficient but restricted to continuous relaxations of discrete design variables. This review examines the cross-field literature on Bayesian optimization with non-standard acquisition strategies — particularly from the combinatorial optimization, drug discovery, and materials science fields — to identify methods for handling discrete design spaces without continuous relaxation. Three directions emerge: (1) applying trust-region BO (TuRBO) from high-dimensional continuous optimization to binary topology domains via discrete kernels, (2) improving GP surrogates with additive or product-kernel structures borrowed from genomics BO literature, and (3) exploring reinforcement learning policy search from robotics as a stretch alternative to surrogate-based methods.

---

## Method-Family Landscape

### From High-Dimensional Continuous Optimization

Bayesian optimization methods designed for high-dimensional continuous spaces (>100 dimensions) offer the most direct transfer path. Trust-region BO (TuRBO) [1] decomposes the search space into local trust regions, reducing the effective dimensionality. SAASBO [2] uses sparsity-inducing priors to identify the most relevant dimensions.

### From Combinatorial Optimization (Drug Discovery, Materials Science)

Drug discovery BO routinely operates over discrete molecular graphs and categorical feature spaces [3, 4]. The COMBO method [5] defines graph kernels over combinatorial spaces, providing a direct analog for binary topology problems. Materials science BO for discrete crystal structure search [6] uses discrete diffusion models as surrogate proposals.

### From Robotics and Reinforcement Learning

Policy-gradient methods from robotics [7] treat the topology layout as a policy parameter sequence, bypassing the surrogate model entirely. This is a fundamentally different paradigm but relevant when evaluation budgets permit 1000+ samples.

---

## Per-Paper Summary Blocks

### [Eriksson et al., 2019] — Scalable Global Optimization via Local Bayesian Optimization (TuRBO)

**Assumptions** — Response surface is locally smooth within trust regions even if globally multimodal. Trust region size adapts based on success/failure history. Assumes continuous design variables with L∞ distance metric.

**Outputs / Contributions** — TuRBO algorithm with adaptive trust region mechanism. Benchmarks on 200-dimensional continuous test functions and rover trajectory optimization. Demonstrated 10× improvement over standard BO at high dimensionality.

**Gaps / Limitations** — Trust region mechanism assumes continuous variables; no direct mechanism for binary domains. Acquisition function optimization (Thompson sampling) requires dense continuous space. Performance on discrete or mixed spaces not demonstrated.

**Cross-Field Transfer Potential** — TuRBO's local decomposition strategy transfers to discrete topology if the trust region is redefined over Hamming-distance neighborhoods of binary vectors. The success/failure adaptation mechanism is domain-agnostic. High transfer potential for large-scale topology problems (>500 elements).

---

### [Eriksson & Jankowiak, 2021] — High-Dimensional Bayesian Optimization with Sparse Axis-Aligned Subspaces (SAASBO)

**Assumptions** — True function depends on a sparse subset of input dimensions. Sparsity prior (half-Cauchy) on lengthscales identifies relevant dimensions automatically. Assumes continuous differentiable response.

**Outputs / Contributions** — SAASBO with sparse GP prior. Full posterior inference via MCMC (NUTS). Demonstrated effective dimensionality identification in 100–1000 dimensional spaces. Open-source implementation (BoTorch).

**Gaps / Limitations** — MCMC inference is computationally expensive (10–100× slower than MAP estimation). Sparsity prior assumes additive dimension importance — not applicable when interactions between discrete topology elements dominate performance.

**Cross-Field Transfer Potential** — Moderate. Sparsity identification useful if a subset of topology elements drives structural performance. MCMC cost may be prohibitive within a 200-evaluation budget. Most useful for identifying which regions of the topology domain matter before switching to a local search.

---

### [Gomez-Bombarelli et al., 2018] — Automatic Chemical Design Using a Data-Driven Continuous Representation of Molecules (VAE-BO)

**Assumptions** — Discrete molecular graphs can be embedded in a continuous latent space via variational autoencoder. BO operates in the continuous latent space; decoder maps back to discrete structures. Requires pre-training data covering the relevant chemical space.

**Outputs / Contributions** — End-to-end framework: VAE encoder/decoder + GP surrogate in latent space + BO acquisition. Demonstrated on drug-like molecule optimization. First demonstration of BO over discrete molecular graphs via continuous latent space.

**Gaps / Limitations** — Requires large pre-training dataset of discrete structures (10,000+ molecules). Decoder may not be invertible — not every latent point decodes to a valid discrete structure. Validity constraint not enforced during acquisition. Pre-training data requirement is prohibitive for novel engineering domains without prior topology databases.

**Cross-Field Transfer Potential** — High conceptual transfer: topology layouts can be encoded as binary images → VAE → continuous latent space → BO. The pre-training requirement is the main barrier; could be addressed with a smaller-scale pre-training corpus of SIMP solutions. Architecture must enforce structural validity (connected load paths).

---

### [Baptista & Poloczek, 2018] — Bayesian Optimization of Combinatorial Structures (COMBO)

**Assumptions** — Design space is a graph (nodes = design choices, edges = adjacency). Graph kernel (diffusion kernel) measures similarity between discrete structures. Assumes the response function is smooth with respect to graph distance.

**Outputs / Contributions** — COMBO: BO algorithm using graph diffusion kernels over combinatorial spaces. No continuous relaxation required. Demonstrated on binary neural architecture search, Ising models, and contamination problems. Graph kernel computation scales as O(N²) in number of candidate structures.

**Gaps / Limitations** — Graph kernel computation is expensive for large combinatorial spaces (>10,000 elements). Requires explicit enumeration or random sampling of candidate structures — not scalable to topology problems with millions of potential layouts. No demonstrated application to structural mechanics.

**Cross-Field Transfer Potential** — Highest among discrete BO methods for direct application to binary topology. Graph kernel is domain-agnostic. Scalability is the primary challenge; approximations (Nyström, sparse GPs) may reduce cost. Strongest candidate for a direct port to small-scale topology problems (≤500 binary elements).

---

## Assumption Map

| Assumption | Papers | Violation Risk in Topology |
|-----------|--------|--------------------------|
| Smooth continuous landscape | TuRBO [1], SAASBO [2] | HIGH — binary topology creates combinatorial jumps |
| Sparse dimension importance | SAASBO [2] | MEDIUM — structural performance may depend on global topology patterns |
| Continuous latent space validity | VAE-BO [3] | HIGH — not all latent points decode to structurally valid topologies |
| Graph distance ~ function distance | COMBO [5] | MEDIUM — Hamming distance over binary layouts may not correlate with compliance |

---

## Sim-to-Real Summary

| Paper | Validation Type | Hardware Validated? |
|-------|---------------|-------------------|
| TuRBO [1] | Simulation + physical benchmark functions | No (rover = simulation) |
| SAASBO [2] | Simulation only | No |
| VAE-BO [3] | Wet-lab synthesis of top candidates | Yes (chemistry, not structural) |
| COMBO [5] | Simulation only | No |

**Gap**: No retrieved paper demonstrates BO for discrete topology optimization with hardware-validated structural testing.

---

## Representation Audit

All BO methods surveyed represent topology as binary vectors or graphs. None use mesh-based or field-based representations. The binary vector representation does not encode spatial adjacency, which may explain poor GP surrogate performance — COMBO's graph kernel is the only approach that explicitly models spatial structure.

---

## Gap Analysis

**Standard gaps from synthesis:**
- No BO method has been demonstrated on large-scale 3D discrete topology (>10,000 binary variables)
- No acquisition function natively handles structural validity constraints (connected load paths)
- No benchmarks against SIMP on equivalent topology problems

**Gaps from Research Frame `failure_modes[]`:**
- **[UNADDRESSED GAP]** No retrieved paper addresses: "GP surrogate assumes smooth continuous landscape — discrete variables create combinatorial jumps." COMBO uses a graph kernel instead of a GP, which partially addresses this, but no paper directly benchmarks GP vs. graph kernel on binary topology.
- **[UNADDRESSED GAP]** No retrieved paper addresses: "Acquisition function optimization becomes NP-hard over binary domains." COMBO samples candidates randomly; TuRBO uses Thompson sampling over continuous space. No paper proposes an efficient NP-hard acquisition optimizer for binary topology.
- *Partially addressed*: "Surrogate model accuracy degrades rapidly with dimensionality (>200 elements)." TuRBO and SAASBO address high-dimensional continuous spaces but not discrete spaces.

---

## Research Agenda

Each direction is framed as:
**Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain].**

### Direction — highest tractable
**Apply/improve COMBO (graph diffusion kernel BO) from combinatorial optimization to solve discrete variable handling in Bayesian topology optimization for aerospace structural compliance minimization.**
- **Why this method**: COMBO's graph kernel explicitly models similarity between binary layouts using diffusion distance, directly addressing the GP smoothness assumption violation. The kernel is domain-agnostic and does not require pre-training data.
- **Source papers**: [5], [1], [4]
- **Adaptation required**: Define a graph topology over binary element arrays where nodes are elements and edges encode spatial adjacency; compute diffusion kernel over this graph; integrate with BoTorch acquisition functions. Scale Nyström approximation for problems >500 elements.
- **Evidence of feasibility**: COMBO demonstrated on binary neural architecture search (similar combinatorial structure). Diffusion kernels are established in graph ML literature. No structural mechanics application yet — represents a genuine contribution.
- **First experiment a researcher would run**: Implement COMBO with spatial adjacency graph on a 2D MBB beam (80×40 binary elements, 3200 variables). Compare compliance achieved at 300 evaluations against SIMP baseline and standard GP-BO. Target: COMBO matches SIMP within 15% compliance at same evaluation budget.

### Direction — medium
**Apply/improve VAE + continuous latent space BO from drug discovery to solve the lack of differentiable surrogate landscape in discrete topology optimization for aerospace structural design.**
- **Why this method**: The VAE-BO framework from drug discovery demonstrates that BO can operate effectively in a continuous latent space learned from discrete structures. The key insight — that the surrogate need not operate in the original discrete space — transfers directly to topology optimization.
- **Source papers**: [3], [2]
- **Adaptation required**: Train a convolutional VAE on a corpus of SIMP solutions (≥5000 topologies across load cases); enforce structural validity via a differentiable connectivity constraint in the decoder loss; operate GP-BO in the 32–64 dimensional latent space; decode final recommendations to binary layouts for FEM evaluation.
- **Evidence of feasibility**: VAE-BO demonstrated in drug discovery with comparable pre-training corpus sizes. Convolutional VAEs for binary image generation are mature. Structural validity enforcement is novel but analogous to chemical validity constraints (REINFORCE-style penalization).
- **First experiment a researcher would run**: Train a 2D convolutional VAE on 10,000 SIMP solutions (varying load cases, volume fractions). Run 200-iteration BO in latent space. Measure: (a) fraction of decoded layouts that are structurally valid (connected load path), (b) best compliance found vs. SIMP at same evaluation count.

### Direction — stretch-exploratory
**Apply/improve policy gradient RL from robotics to solve the sequential topology refinement problem in aerospace structural optimization, bypassing the surrogate model entirely.**
- **Why this method**: Policy-gradient methods (PPO, SAC) from robotics treat sequential decision-making over discrete action spaces without requiring a smooth surrogate. For topology optimization framed as a sequential element-inclusion policy, RL offers a surrogate-free alternative that scales to large binary spaces.
- **Source papers**: [7]
- **Adaptation required**: Frame topology optimization as a sequential MDP: state = current topology + compliance; action = add/remove one element; reward = compliance improvement per evaluation. Requires ~1000+ FEM evaluations per training run — currently beyond typical aerospace budgets.
- **Evidence of feasibility**: RL for combinatorial optimization (TSP, chip placement) is demonstrated at similar action-space scales. Chip placement RL (Google, 2021) operates over ~10,000 discrete placements — comparable to medium-scale topology problems. Evaluation cost per step is the primary barrier.
- **First experiment a researcher would run**: Implement PPO on a 2D MBB beam with a fast surrogate FEM (reduced-order model) as the environment. Target: 1000 RL episodes at <1 second per episode (surrogate FEM). Measure: compliance convergence vs. wall-clock time compared to SIMP. This direction is **exploratory and requires foundational validation** — the surrogate-FEM accuracy must be characterized before claims about structural performance can be made. Does not extend to multi-material optimization per `scope_boundaries[]`.

---

## References

[1] Eriksson, D., Pearce, M., Gardner, J., Turner, R. D., & Poloczek, M. (2019). Scalable global optimization via local Bayesian optimization. NeurIPS 2019.

[2] Eriksson, D., & Jankowiak, M. (2021). High-dimensional Bayesian optimization with sparse axis-aligned subspaces. UAI 2021.

[3] Gomez-Bombarelli, R., Wei, J. N., Duvenaud, D., Hernandez-Lobato, J. M., Sanchez-Lengeling, B., Sheberla, D., ... & Aspuru-Guzik, A. (2018). Automatic chemical design using a data-driven continuous representation of molecules. ACS Central Science, 4(2), 268–276.

[4] Griffiths, R. R., & Hernandez-Lobato, J. M. (2020). Constrained Bayesian optimization for automatic chemical design using variational autoencoders. Chemical Science, 11(2), 577–586.

[5] Baptista, R., & Poloczek, M. (2018). Bayesian optimization of combinatorial structures. ICML 2018.

[6] Zunger, A. (2018). Inverse design in search of materials with target functionalities. Nature Reviews Chemistry, 2(4), 1–16.

[7] Mirhoseini, A., Goldie, A., Yazgan, M., Jiang, J. W., Songhori, E., Wang, S., ... & Dean, J. (2021). A graph placement methodology for fast chip design. Nature, 594(7862), 207–212.

---

*AI Disclosure: This example was produced with AI-assisted research tools (deep-research v4.0) for demonstration and smoke-test purposes. It is a synthetic walkthrough, not a real literature review.*
