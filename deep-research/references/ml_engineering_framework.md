# ML-for-Engineering Framework Reference

## Purpose

This reference supports method selection justification, assumption identification, and literature organization for research at the intersection of machine learning and mechanical engineering design. It is read by the `research_architect_agent` and `synthesis_agent` when analyzing or designing ML-for-engineering studies.

---

## Routing Reminder

This reference now supports a **conditional front-end**:

- **Physics-heavy topics**: start with physics system, cheapest usable data source, fidelity ladder, acquisition bottlenecks, and representation.
- **Representation-sensitive topics**: isolate the encoding bottleneck before comparing method families.
- **Method-first topics**: allow direct method-family comparison, then use the tables below to explain what assumptions would change the ranking.

This front-end does **not** replace the stable backend of model-family / assumption-lineage analysis. It clarifies which method-family comparisons are even meaningful.

---

## Part 0: Data-Acquisition Regime Taxonomy

Before choosing a method family, identify how the evidence is actually acquired.

| Acquisition regime | Typical source | Speed / cost profile | What it is good for | Common failure mode |
|---|---|---|---|---|
| Analytic / synthetic | closed-form solutions, manufactured solutions, toy generators | Fastest / cheapest | sanity checks, proof-of-concept stress tests | too simple to reflect engineering deployment |
| Reduced-order / surrogate-of-simulator | ROMs, coarse solvers, simplified physics | Fast / cheap | broad search, rapid ablations, pretraining | systematic bias vs full physics |
| Low-fidelity simulation | coarse CFD/FEM, simplified boundary conditions | Moderate speed / moderate cost | trend capture, screening large design sets | wrong local ranking in critical regions |
| High-fidelity simulation | fine CFD/FEM, expensive multiphysics solvers | Slow / expensive | trustworthy offline supervision, benchmark targets | too expensive for dense search or repeated ablation |
| Hardware / experiment | physical tests, in-situ sensing, bench rigs | Slowest / most expensive | canonical validation, sim-to-real truth | sparse data, instrumentation noise, limited coverage |
| Mixed-fidelity | low + high fidelity + experiments | Variable | data-efficient design under realistic budgets | poor correlation between fidelity levels |

Questions to record before method selection:
- What is the **cheapest usable data source**?
- What is the **fidelity ladder**?
- What is the **acquisition bottleneck**: money, solver time, labeling, instrumentation, or scarce hardware access?
- Which conclusions are valid at each fidelity level?

---

## Part 1: Method Selection Guide

The right ML method is determined by three things: how much data you have (and how expensive it is to get more), what the application needs from the model (uncertainty, interpretability, physics consistency), and what the problem structure looks like.

The following tables are for quick lookup. Always document which of these factors drove your selection.

### Data Regime -> Method Family

| Data Regime | Typical Scenario | Primary Method Family | Backup / Alternative |
|-------------|-----------------|----------------------|---------------------|
| < 50 training points, experiments expensive | Physical testing, each run costs $$$ | Gaussian Process (Bayesian optimization) | Co-kriging (if multi-fidelity available) |
| 50-500 samples, mix of sim + experiments | Moderate-fidelity CFD + some tests | Multi-fidelity surrogate (co-kriging, MF-NN) | GP + low-fidelity correction |
| 500-10K samples, simulation only | Automated FEM/CFD, batch runs | Neural network surrogate (MLP, ResNet) | Random forest (if interpretability needed) |
| 10K+ samples, sim or large dataset | High-throughput simulation, digital twin | Deep learning (CNN for fields, GNN for meshes) | PINN if physics structure is known |
| Sequential / iterative data | Online design optimization, closed loop | Bayesian optimization (BO) + surrogate | Reinforcement learning (if rewards available) |
| Rich unlabeled + sparse labeled | Transfer from simulation, limited experiments | Transfer learning / domain adaptation | Semi-supervised + physics regularization |

### Application Requirement -> Method Family

| What the application needs | Method family | Rationale |
|---------------------------|--------------|-----------|
| Calibrated uncertainty (for sequential optimization) | Gaussian process, Bayesian NN, deep ensemble | BO acquisition functions require calibrated uncertainty to be valid |
| Interpretability / explainability | Linear surrogate, sparse regression, symbolic regression | Engineering decisions often require human-readable models |
| Physics consistency (satisfies PDE, conservation laws) | Physics-Informed NN (PINN), hybrid mechanistic-ML | Hard constraints on output; unconstrained NN may violate physics |
| Topology / shape generalization | Graph NN, implicit neural representation, latent shape model | Parameterized representations cannot change connectivity |
| Multi-objective output | Multi-output GP, vector-valued NN with correlated outputs | Scalar surrogate per objective loses correlations |
| Extrapolation beyond training distribution | PINN, mechanistic model + ML correction | Pure ML interpolates; physics carries extrapolation |
| Scalability to high-dim input | Sparse GP (inducing points), dimensionality reduction + GP | Standard GP is O(n^3); sparse approximations handle large n |

---

## Part 2: Method Assumption Catalog

Every ML method makes assumptions. Limitations that appear in experiments are almost always traceable to one of these assumptions failing. Use this catalog when mapping limitations to assumption roots.

### Gaussian Process Regression

**Core assumptions:**
- **Stationarity**: covariance depends only on the distance between points, not their location. Fails for problems where local structure varies across the design space (e.g., a design space with a sharp optimum in one region and flat in another).
- **Smoothness**: the kernel lengthscale controls how smooth the latent function is assumed to be. Fails for discontinuous or near-discontinuous responses (e.g., flow separation onset).
- **Gaussian observation noise**: residuals are i.i.d. Gaussian. Fails for heavy-tailed noise or structured noise from simulation solver variability.
- **Finite-dimensional input**: standard GP is not defined for variable-topology inputs. Fixed-dimensionality CAD parameters only.

**Holds when**: smooth, low-to-moderate dimensional design spaces (< ~20 dims practical without sparse approximation), few training points, response surface is unimodal or mildly multi-modal.

**Breaks when**: high-dimensional, multi-modal, discrete design features, topological variation, heavy-tailed noise.

**Relaxations in the literature**:
- Stationarity -> Deep Kernel Learning (neural network feature map before GP kernel)
- High dimensionality -> Sparse GP / inducing points / KISS-GP
- Non-Gaussian likelihood -> Laplace approximation, expectation propagation
- Variable topology -> cannot be fixed within GP family; switch to GNN or latent shape model

---

### Neural Network Surrogate (MLP / CNN / ResNet)

**Core assumptions:**
- **Sufficient i.i.d. training data**: NN interpolates from training data; with < ~200 samples the model is likely over-parameterized or underfit depending on architecture.
- **Fixed input/output dimensionality**: standard MLP requires fixed-size input. Cannot handle variable-topology designs without a fixed-dim encoding step.
- **No calibrated uncertainty** (vanilla NN): point predictions only. Bayesian NN or deep ensembles needed for uncertainty.
- **Stationarity of input distribution**: if test inputs are drawn from a different distribution than training inputs, generalization fails.

**Holds when**: large simulation budget (thousands of runs), fixed design parameterization, complex nonlinear response where GP smoothness assumption is violated.

**Breaks when**: sparse data, need calibrated uncertainty, topological design changes, OOD queries.

**Relaxations**:
- Uncertainty -> Bayesian NN, Monte Carlo dropout, deep ensembles
- Physics consistency -> PINN (adds PDE residual loss)
- Sparse data -> transfer learning from related simulation domain

---

### Physics-Informed Neural Network (PINN)

**Core assumptions:**
- **Known governing PDE**: the physics must be expressible as a differential equation that can be evaluated at collocation points.
- **Differentiable simulation**: automatic differentiation through the physics residual requires that the PDE be differentiable.
- **PDE is correct**: if the governing equation is approximate or unknown, baking it in as a hard constraint can degrade performance relative to pure data.
- **No multi-scale**: standard PINN struggles with multi-scale problems where the PDE has very different behavior at different scales.

**Holds when**: physics is well-understood and can be written as a PDE, some training data is scarce but physics covers the gaps, need extrapolation beyond training data.

**Breaks when**: governing physics is unknown or stochastic, turbulence / chaotic dynamics, large multi-scale problems, experimental data contradicts assumed PDE.

---

### Multi-Fidelity Surrogate (Co-Kriging / MF-NN)

**Core assumptions:**
- **Correlated fidelities**: low-fidelity model captures the trend of the high-fidelity response. If low-fidelity is systematically biased in certain regions, co-kriging propagates that bias.
- **Stationary correlation between fidelities**: the relationship between fidelity levels is assumed to be consistent across the design space.
- **Known fidelity levels**: each data point must be labeled with its fidelity level. Partially known fidelity is not handled.

**Holds when**: cheap simulation (low-fidelity) and expensive simulation or experiment (high-fidelity) are available; low-fidelity captures at least the qualitative trend.

**Breaks when**: low-fidelity solver fails to capture the relevant physics (e.g., inviscid CFD for separated flows), large systematic bias, unknown fidelity gaps.

---

### Bayesian Optimization (BO)

**Core assumptions:**
- **Surrogate is calibrated**: BO acquisition functions (UCB, EI, PI) are only valid if the surrogate's uncertainty is calibrated. A surrogate that reports high confidence where it is actually wrong will lead BO to skip good regions.
- **Black-box objective**: BO assumes no gradient information. If gradients are available, gradient-based methods are likely more efficient.
- **Finite, bounded search space**: standard BO operates on a fixed compact domain. Extensions exist for unbounded or structured spaces.
- **Noiseless or Gaussian-noisy observations**: standard BO with GP assumes observations have Gaussian noise with known variance.

**Holds when**: objective is expensive, gradient-free, low-to-moderate dimensional (< ~20 dims practical), smooth enough for GP surrogate.

**Breaks when**: high-dimensional (> 20 continuous dims), highly multi-modal (acquisition function fails to find global optimum), objective is cheap (BO overhead not justified), structured discrete space (standard BO not defined).

---

### Domain Adaptation / Transfer Learning (Sim-to-Real)

**Core assumptions:**
- **Shared latent structure**: source (simulation) and target (hardware) share a latent representation -- only the marginal distribution over inputs/outputs differs.
- **Covariate shift**: the conditional distribution P(output | input) is the same across domains; only P(input) differs. If the conditional distribution also changes (concept shift), standard domain adaptation fails.
- **Target domain accessible**: most adaptation methods need some unlabeled (or a few labeled) target domain samples. Zero-shot sim-to-real is possible only with domain randomization.

**Holds when**: sim and hardware share the same underlying physics; gap is mostly sensor noise, actuator variation, or unmodeled friction.

**Breaks when**: fundamental physics is missing from simulation (e.g., aerodynamic simulator ignores material flexibility), sim-to-real gap is too large for the shared latent structure assumption to hold.

---

## Part 3: Sim-to-Real Gap Taxonomy

The sim-to-real gap in ML-for-engineering refers to the performance degradation when a model trained on simulation data is deployed on physical hardware. It has distinct sources -- identifying which source is present determines the appropriate mitigation.

### Gap Type 1: Sensor and Actuator Discrepancy

**Description**: The simulation assumes perfect sensors and actuators; hardware has noise, delay, hysteresis, and calibration error.

**Diagnostic**: Model works in sim, fails specifically when sensor readings are noisy or when actuator response lags input.

**Mitigations**: Domain randomization over sensor noise parameters; system identification for actuator dynamics; Kalman filtering before model inference.

---

### Gap Type 2: Unmodeled Physics

**Description**: The simulation omits physical phenomena that matter in reality -- flexible body dynamics, contact mechanics, turbulence, thermal effects, material nonlinearity.

**Diagnostic**: Systematic error that is consistent across hardware trials but absent in simulation; error increases with conditions that activate the unmodeled physics.

**Mitigations**: Physics-informed regularization; residual learning (train a correction model on sim-to-real error); higher-fidelity simulation; model augmentation.

---

### Gap Type 3: Distribution Shift in Inputs

**Description**: Training data from simulation does not cover the distribution of inputs encountered in hardware deployment -- different geometry, material, boundary conditions.

**Diagnostic**: Model performs well on held-out simulation data but poorly on hardware; error increases for hardware conditions at the edge of or outside the simulation distribution.

**Mitigations**: Domain randomization (wide distribution of simulation conditions during training); adaptive sampling (collect physical data in underrepresented regions); uncertainty-guided deployment (use GP uncertainty to flag out-of-distribution inputs).

---

### Gap Type 4: Objective Mismatch

**Description**: The metric optimized in simulation (e.g., drag coefficient in CFD) is not the same as the metric that matters in hardware (e.g., actual flight time, user-perceived comfort).

**Diagnostic**: Model achieves good performance on simulation metric but the engineering goal is not met in deployment.

**Mitigations**: Validate proxy metric correlation before deploying; multi-objective optimization including robustness objectives; hardware-in-the-loop refinement.

---

## Part 4: Representation Problem Taxonomy

The representation problem is the challenge of encoding the engineering design space (geometry, topology, material, boundary conditions) in a form that an ML model can process efficiently and that generalizes beyond the training examples.

### Type 1: Parameterized CAD / Geometry

**Description**: Design is described as a fixed-size vector of parameters (e.g., chord length, twist angle, wall thickness at N points).

**Advantages**: Simple, well-defined input to any ML model; interpretable; differentiable if CAD kernel supports it.

**Limitations**: Cannot represent topological changes (number of holes, connectivity); generalization limited to the parameterization space; high-dimensional for complex shapes.

**When to use**: Optimization of a fixed design template (aerodynamic profile, heat exchanger geometry) where topology is fixed.

---

### Type 2: Mesh / FEM Discretization

**Description**: Design is represented as a mesh -- nodes, elements, connectivity. Used in structural and fluid simulations.

**Advantages**: Natural for FEM; can represent complex geometry; connectivity captures topology.

**Limitations**: Variable mesh size and connectivity makes direct input to standard NNs impossible; must preprocess or use mesh-aware architectures (GNN, U-Net on structured grids).

**When to use**: When simulation output is a field (stress, velocity, temperature) and the model must learn the map from geometry to field.

---

### Type 3: Latent Shape Representation

**Description**: An autoencoder or variational autoencoder learns a continuous latent space of shapes; ML operates in the latent space.

**Advantages**: Continuous, low-dimensional; can interpolate between designs; can represent topological variation if encoder is expressive enough.

**Limitations**: Latent space may not align with physically meaningful dimensions; requires training data to learn the encoder; generalization limited to shapes seen during encoder training.

**When to use**: Generative design, design exploration, topology optimization where parameterization is too restrictive.

---

### Type 4: Graph / Topology-Aware Representation

**Description**: Design is a graph where nodes are geometric features or structural elements and edges are connections.

**Advantages**: Topologically flexible; graph neural networks (GNN) process it naturally; captures connectivity structure.

**Limitations**: Requires defining what constitutes a node and edge, which is domain-specific; GNN training can be expensive; message-passing may miss long-range dependencies.

**When to use**: Truss optimization, circuit layout, robotic kinematic chains, molecular design analogues in engineering.

---

### Type 5: Physics Fields / Solution Snapshots

**Description**: Input to ML is the simulation field itself (velocity field, stress field, temperature distribution) rather than the design parameters.

**Advantages**: Rich information; captures physics at every point; no parameterization needed.

**Limitations**: Very high dimensional; requires mesh alignment or interpolation for different geometries; encoding is expensive.

**When to use**: Surrogate models for field prediction (e.g., predict full stress field from boundary conditions); reduced-order models.

---

### Type 6: Operator Representation

**Description**: Inputs and outputs are treated as functions or fields, and the learning target is an operator rather than a finite-dimensional vector-to-vector map.

**Advantages**: Natural for PDE surrogates across varying boundary conditions or forcing functions; aligns well with FNO/DeepONet-style families.

**Limitations**: Requires care about discretization invariance, mesh transfer, and whether the chosen basis actually captures the relevant physics.

**When to use**: PDE surrogate learning, family-of-solver acceleration, function-space mapping tasks.

---

### Type 7: Multimodal Sensor Fusion

**Description**: The representation combines multiple modalities such as fields, images, time series, scalar process parameters, or in-situ measurements.

**Advantages**: Can capture complementary information that any single modality misses; useful when the bottleneck is partial observability.

**Limitations**: Alignment across modalities is difficult; one weak modality can dominate training artifacts; data collection cost may rise sharply.

**When to use**: Physics-process monitoring, sim-to-real transfer with instrumentation, defect detection plus process-state inference.

---

## Part 4.5: Representation-First Comparison Checklist

Before comparing method families, answer:

1. **What must the representation preserve?**
   - geometry
   - topology
   - boundary conditions
   - physical fields
   - temporal history
2. **What cannot be expressed by the current encoding?**
3. **Is the main bottleneck representation or method family?**
4. **Would a better fidelity mix matter more than a better architecture?**
5. **Does the representation support the validation claim (simulation only / hardware / both)?**

Use this checklist to prevent false method comparisons where the real constraint is upstream in acquisition or encoding.

---

## Part 5: Common Research Patterns in ML-for-Engineering Design

### Pattern 1: Bayesian Optimization for Expensive Engineering Design

**Problem structure**: Optimize a design metric (drag, weight, efficiency) that is evaluated by expensive simulation or physical experiment; gradient information unavailable; budget is tight (< 100 evaluations).

**Standard workflow**: GP surrogate -> acquisition function -> next experiment -> update -> repeat.

**Key papers to know**: Mockus (1975) -- EI acquisition; Snoek et al. (2012) -- Spearmint / BO in ML; Shahriari et al. (2016) -- BO survey; Frazier (2018) -- BO tutorial; engineering applications: Forrester & Keane (2009), Lyu et al. (2019).

**Common failure modes**: Surrogate not calibrated -> BO explores wrong regions; search space too large for GP; problem is multi-modal beyond GP expressiveness.

---

### Pattern 2: Multi-Fidelity Surrogate for Simulation-Heavy Design

**Problem structure**: Have access to both fast/cheap low-fidelity simulation and slow/expensive high-fidelity simulation (or physical tests); want to use both efficiently.

**Standard workflow**: Co-kriging or MF-NN builds surrogate from both fidelity levels; high-fidelity points correct the low-fidelity trend.

**Key papers**: Kennedy & O'Hagan (2000) -- co-kriging; Forrester et al. (2007) -- MF optimization; engineering: Huang et al. (2006), Park et al. (2017).

**Common failure modes**: Low-fidelity is biased (inviscid CFD for separated flow); fidelity levels are inconsistent across design space.

---

### Pattern 3: Physics-Informed Learning for Data-Scarce Engineering

**Problem structure**: Physics is well-understood (governed by known PDE), but experiments are few; want physics to regularize the ML model.

**Standard workflow**: PINN -- add PDE residual loss to data loss; or hybrid model -- mechanistic model for trend, ML for residual.

**Key papers**: Raissi et al. (2019) -- PINN; Karniadakis et al. (2021) -- physics-informed ML review; engineering: Cai et al. (2021) for fluid mechanics PINN.

**Common failure modes**: PDE is approximate or stochastic; multi-scale problems; training instability from competing loss terms.

---

### Pattern 4: Sim-to-Real Transfer for Engineering Control / Robotics

**Problem structure**: Train on simulation (cheap, safe); deploy on hardware (expensive, risk of damage); gap between sim and real must be bridged.

**Standard workflows**: Domain randomization (vary sim parameters widely during training); domain adaptation (train discriminator to align sim and real distributions); residual dynamics learning (model the sim-to-real error with hardware data).

**Key papers**: Tobin et al. (2017) -- domain randomization for robotics; Peng et al. (2018) -- SimToReal for locomotion; engineering: Jakobi et al. (1995) -- sim-to-real early work.

**Common failure modes**: Gap too large for domain randomization to bridge; adaptation requires too much hardware data; unmodeled contact physics.

---

### Pattern 5: Generative Design / Topology Optimization with ML

**Problem structure**: Optimize the topology (shape and material distribution) of a structure for given loading conditions; design space is combinatorially large.

**Standard workflows**: SIMP (density-based) -- classical; ML acceleration of SIMP; generative models (VAE, GAN, diffusion) for design generation; GNN for irregular meshes.

**Key papers**: Sigmund & Maute (2013) -- SIMP review; Oh et al. (2019) -- deep generative models for design; Wang et al. (2020) -- deep learning for topology optimization.

**Common failure modes**: Generated designs not manufacturable; ML model not aware of physics constraints; latent space doesn't capture mechanically meaningful variation.
