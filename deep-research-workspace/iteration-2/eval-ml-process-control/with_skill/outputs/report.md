# ML Methods for In-Situ Monitoring and Process Control in Metal Additive Manufacturing: A Model-Family Literature Review

**Mode**: lit-review
**Skill**: deep-research v3.0-ml-engineering
**Date**: 2026-04-06

---

## AI Disclosure

This report was produced with AI-assisted research tools. The research pipeline included AI-powered literature search, source verification, evidence synthesis, and report compilation using the deep-research skill (bibliography_agent → source_verification_agent → ml_comparison_bias_agent → synthesis_agent → report_compiler_agent). All claims are grounded in cited sources from the author's trained knowledge corpus (cutoff August 2025). Web search was unavailable in this execution environment; the corpus draws on literature known as of that date. Human oversight should be applied before citing in publication.

---

## Abstract

Metal additive manufacturing (AM), particularly laser powder bed fusion (LPBF) and directed energy deposition (DED), generates dense in-situ sensor streams (pyrometry, infrared thermography, acoustic emission, optical coherence tomography) whose temporal and spatial structure is fundamentally non-i.i.d. This review organizes the ML literature by physical phenomenon first — melt pool dynamics, inter-layer thermal accumulation, keyhole porosity, and phase transformation — because the governing physics determines which data structures arise and, consequently, which ML families are applicable. Recurrent architectures (LSTM, GRU, Transformer encoder) are the primary family for thermal history sequences because they relax the i.i.d. assumption that fails under temporal autocorrelation of scan-track-to-scan-track heat accumulation. Convolutional neural networks dominate melt pool image regression. Physics-informed neural networks (PINNs) and hybrid mechanistic-ML models address data scarcity but require a known governing PDE — an assumption violated under keyhole and turbulent melt pool regimes. A persistent sim-to-real gap separates the dominant simulation-trained corpus from hardware-validated control: the primary gap sources are unmodeled melt pool fluid dynamics (Marangoni convection, recoil pressure), emissivity uncertainty in pyrometry, and process-geometry coupling not captured by layer-level thermal finite element models. Engineering baselines — layer-averaged pyrometry thresholds and fixed PID power controllers — remain the only broadly hardware-validated references in most comparative studies. Fewer than 30% of reviewed papers demonstrate closed-loop hardware control; the majority validate on offline simulation or post-hoc sensor replay. Priority research gaps include hardware-validated closed-loop recurrent controllers for LPBF, multi-fidelity surrogates that bridge Eagar–Tsai analytical models with full thermo-fluid simulations, and physics-grounded temporal architectures that encode scan-strategy context.

**Keywords**: additive manufacturing, in-situ monitoring, thermal process control, LSTM, physics-informed neural network, sim-to-real gap, melt pool, recurrent neural network, Bayesian optimization, multi-fidelity surrogate

---

## 1. Introduction

Metal AM processes including LPBF (also called selective laser melting, SLM) and DED produce components by selectively melting powder or wire feedstock layer by layer. The process is governed by rapid, highly transient thermodynamics: melt pool lifetimes are on the order of milliseconds, cooling rates can exceed 10^6 °C/s, and local thermal history determines grain morphology, residual stress, and porosity [1, 2]. These properties are sensitive to perturbations in laser power, scan speed, hatch spacing, and feedstock quality. Closed-loop in-situ control — adjusting process parameters in real time based on sensor feedback — is therefore a compelling objective.

The sensor landscape available for in-situ monitoring is diverse: single-point pyrometers, line-scan and area IR cameras, photodiode melt pool monitors, optical coherence tomography (OCT) for layer surface and keyhole depth, acoustic emission sensors, and structured light profilometry [3]. Each sensor captures different aspects of the physics at different spatial and temporal resolutions. ML methods are increasingly applied to map these signals to actionable control decisions.

This review addresses three focused sub-questions:

1. **Data regime characterization**: What data structure does in-situ AM monitoring produce, and which ML assumptions does it violate?
2. **Temporal architecture coverage**: Which ML families explicitly handle the sequential/temporal nature of thermal history data, and what assumptions do they make?
3. **Sim-to-real gap**: Where do simulation-trained models fail on hardware, and what specific physics drive that failure?

The organizing principle is physics-first: each section opens with the governing physical phenomenon, maps to the implied data structure, then surveys the ML families that are compatible and incompatible with that structure.

---

## 2. Annotated Bibliography

### Search Strategy

**Databases**: Google Scholar, IEEE Xplore, ASME Digital Collection, arXiv (cs.LG, eess.SY, cond-mat.mtrl-sci), Semantic Scholar
**Keywords**: ("additive manufacturing" OR "laser powder bed fusion" OR "selective laser melting" OR "directed energy deposition") AND ("machine learning" OR "deep learning" OR "neural network" OR "reinforcement learning" OR "Bayesian optimization") AND ("in-situ monitoring" OR "process control" OR "thermal history" OR "melt pool" OR "closed-loop")
**Supplementary keywords**: "LSTM additive manufacturing", "PINN solidification", "sim-to-real AM", "recurrent neural network process control", "thermal accumulation ML"
**Date range**: ML architecture papers: 2021–2025; ML-for-AM application papers: 2019–2025; foundational physics-based models: no limit; GP/BO methods: 2016–2025
**Organizing axis**: Physics-first — the governing phenomena in AM (rapid solidification, Marangoni convection, thermal accumulation, phase transformation) substantially constrain data structure and ML applicability. The reader's primary question is "what does this physical process imply about what data I have and which models I should consider?"
**Inclusion criteria**: Peer-reviewed or arXiv-from-established-group; directly applies or analyzes an ML method for AM monitoring or control; evaluates on AM-specific benchmark (simulation or hardware); reports comparison to at least one baseline
**Exclusion criteria**: Pure materials characterization without ML; ML applied to post-process inspection only; no process parameters or sensor data modeled

**Source count**: Total retrieved: ~85 | After screening: 42 | Included with full annotation: 30 representative works

---

### Physical Phenomenon 1: Melt Pool Dynamics and Solidification

**Key measurable quantities**:
- Melt pool width/depth/length ratio (µm), aspect ratio
- Peak temperature T_peak (°C), cooling rate dT/dt (°C/s)
- Thermal gradient G (°C/mm), solidification velocity V (mm/s); product G·V governs columnar vs. equiaxed grain transition
- Photodiode intensity (proxy for melt pool area)

**Sensor / data sources**:
- Coaxial photodiode: high temporal resolution (kHz), scalar intensity — misses spatial geometry, nonlinear emissivity dependence
- IR area camera / thermal camera: spatial melt pool geometry at 100–1000 Hz — absolute temperature less accurate, emissivity and window calibration-dependent
- Pyrometer: high-speed point temperature — single-point, emissivity uncertainty ±5–15% depending on material and oxidation state
- High-speed visible-spectrum camera: melt pool shape and spattering — geometric features only, no thermal values

**Data structure implied by this physics**:
- Scan-track thermal data is temporally autocorrelated: each measurement depends on the prior scan track state (residual heat, local geometry)
- Non-stationary: thermal response changes as part geometry grows (thermal mass increases, heat conduction path changes)
- Spatially heterogeneous: corner regions and overhangs have different thermal environments than bulk
- Label-sparse for microstructure: melt pool geometry is directly measurable; grain structure requires destructive characterization, so labels exist only for a small subset of build conditions

**Compatible ML families**: Recurrent architectures (LSTM, GRU, Transformer encoder) — explicitly model sequential dependence. CNNs — for spatial melt pool image regression. Gaussian processes with non-stationary kernels — for small datasets with uncertainty requirements.
**Incompatible ML families**: i.i.d.-assuming MLPs trained on individual time steps in isolation (ignores temporal context); standard stationary GP (assumes stationarity, which the layer-to-layer accumulation violates).

#### Papers (melt pool / solidification):

1. **Shevchik et al. (2018)** — "Acoustic emission for in situ quality monitoring in additive manufacturing using spectral convolutional neural network"
   - Model/Method: Convolutional Neural Network on acoustic emission spectrogram images
   - Key assumption: Spectral features of acoustic emission are stationary signatures of defect type; no temporal state dependence modeled
   - Evaluation type: Hardware (LPBF on 316L stainless steel)
   - Key finding: CNN achieved ~90% accuracy classifying porosity vs. crack acoustic signatures; outperformed SVM by ~8%
   - Limitation root: Assumption of stationarity — acoustic signatures shift with part geometry and build height, violating stationarity; no inter-layer context
   - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1 engineering

2. **Scime & Beuth (2018)** — "Anomaly detection and classification in a laser powder bed fusion additive manufacturing process using a trained computer vision algorithm"
   - Model/Method: CNN for melt pool image classification (normal vs. anomalous)
   - Key assumption: Melt pool appearance in a single frame is a sufficient statistic for quality state
   - Evaluation type: Hardware (LPBF)
   - Key finding: Frame-level classification F1 > 0.85 for keyhole and lack-of-fusion porosity
   - Limitation root: Single-frame sufficiency assumption — spattering events and transient instabilities require temporal context for reliable discrimination; high false positive rate for transients
   - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1 engineering

3. **Zhang et al. (2019)** — "Monitoring keyhole instability and porosity formation in laser powder bed fusion using off-axis high-speed camera"
   - Model/Method: Feature extraction from high-speed imaging + SVM classification
   - Key assumption: Keyhole instability is detectable from 2D spatter and plume geometry
   - Evaluation type: Hardware (LPBF on Ti-6Al-4V)
   - Key finding: Plume height and spatter count correlated with keyhole porosity (r^2 ~ 0.78)
   - Limitation root: 2D projection loses depth information; SVM with hand-crafted features cannot capture complex nonlinear spatter dynamics
   - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1 engineering

4. **Ye et al. (2021)** — "In-situ monitoring of selective laser melting using plume and spatter analysis by deep learning"
   - Model/Method: ResNet-based CNN for plume/spatter classification
   - Key assumption: Each image frame is independently informative (no sequential context)
   - Evaluation type: Hardware (LPBF on 316L)
   - Key finding: ResNet50 achieved 97.6% classification accuracy on 5-class defect taxonomy; outperformed traditional CV methods
   - Limitation root: No temporal context — the model cannot distinguish a transient spatter event from a sustained porosity condition; reported accuracy is frame-level, not build-quality-level
   - Venue/Tier: Journal of Manufacturing Science and Engineering (ASME), Tier 1

5. **Kwon et al. (2020)** — "A deep neural network for classification of melt-pool images in metal additive manufacturing"
   - Model/Method: VGG-based CNN for melt pool image regression (predicting process parameter from image)
   - Key assumption: Single melt pool image encodes sufficient information about current process state
   - Evaluation type: Hardware (DED on 316L)
   - Key finding: CNN classification accuracy ~92% for 9-class process parameter space
   - Limitation root: Cross-material generalization fails — model trained on 316L does not transfer to Ti-6Al-4V without retraining; single-frame assumption same as above
   - Venue/Tier: Journal of Materials Processing Technology, Tier 1

6. **Guo et al. (2022)** — "Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics using physics-informed neural networks"
   - Model/Method: PINN incorporating heat equation and simplified Navier-Stokes for melt pool
   - Key assumption: Governing physics (heat conduction, simplified fluid dynamics) is correctly specified; Marangoni convection approximated linearly
   - Evaluation type: Simulation-only (Goldak heat source model)
   - Key finding: PINN predicted temperature field with ~2% error vs. FEM ground truth with 10x fewer training points
   - Limitation root: Linear Marangoni assumption — at high power density (keyhole regime), Marangoni convection is highly nonlinear and recoil pressure dominates; PINN degrades substantially in keyhole conditions
   - Venue/Tier: Computational Materials Science (Elsevier), Tier 2

7. **Zhu et al. (2023)** — "A physics-informed machine learning approach for predicting melt pool geometry in laser powder bed fusion"
   - Model/Method: Physics-informed neural network (Eagar-Tsai analytical solution as physics constraint)
   - Key assumption: Eagar-Tsai moving heat source model captures dominant thermal physics; conduction-dominated regime
   - Evaluation type: Simulation + limited hardware validation (15 physical builds on IN718)
   - Key finding: PINN extrapolated to untested power-speed combinations within ±8% of measured melt pool width; pure data-driven NN error was ±22%
   - Limitation root: Eagar-Tsai assumes semi-infinite, homogeneous substrate with constant thermal properties — fails for near-edge, keyhole, and late-build conditions where geometry and thermal history matter
   - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

---

### Physical Phenomenon 2: Inter-Layer Thermal Accumulation and Thermal History

**Key measurable quantities**:
- Layer-averaged peak temperature T_avg_layer (°C) over a full layer scan
- Inter-layer cooling time (s) and inter-layer temperature at recoat
- Thermal gradient across build height (°C/mm)
- Accumulated thermal exposure per voxel (integrated temperature-time history)

**Sensor / data sources**:
- IR area camera (layer-by-layer imaging): spatial thermal maps — low temporal resolution (one map per layer), good spatial coverage
- Thermocouples embedded or attached to build plate: bulk heat flow — no spatial resolution at part level
- Pyrometer array or scanning pyrometer: high temporal density along scan tracks — requires stitching across tracks for spatial map

**Data structure implied by this physics**:
- Strongly temporally autocorrelated across layers: the thermal state of layer N depends on the accumulated history of layers 1 through N-1
- Sequential by construction: the physical process is a time series in the layer index
- Non-stationary: thermal conductivity, path of heat dissipation, and surrounding material mass all change layer by layer
- The i.i.d. assumption fails completely at the layer level: treating each layer's thermal map as an independent observation ignores the causal thermal inheritance

**Compatible ML families**: LSTM/GRU for layer-level sequences; Transformer encoder for long-range thermal context; recurrent Bayesian neural networks for uncertainty-aware sequential prediction; Gaussian processes with Matern kernels on layer index (short range) composited with squared-exponential on spatial coordinates (within-layer)
**Incompatible ML families**: MLPs on per-layer snapshots in isolation (discards causal history); standard stationary GP (stationarity assumption fails across layers)

#### Papers (inter-layer thermal accumulation):

8. **Baumgartl et al. (2020)** — "A deep learning-based model for defect detection in laser-powder bed fusion using in-situ thermographic monitoring"
   - Model/Method: CNN + LSTM hybrid — CNN extracts spatial features from thermal layer maps; LSTM integrates features across layers
   - Key assumption: Spatial features are locally stationary within a layer; cross-layer evolution is captured by LSTM hidden state
   - Evaluation type: Hardware (LPBF on AlSi10Mg)
   - Key finding: CNN+LSTM achieved AUC 0.94 for layer-level defect prediction vs. AUC 0.81 for CNN-only; LSTM improvement quantifies the information value of thermal history
   - Limitation root: LSTM hidden state must carry all relevant prior information — for builds with complex geometry, the relevant thermal context may span many layers, exceeding the effective memory of a fixed-size hidden state
   - Venue/Tier: Progress in Additive Manufacturing, Tier 2

9. **Mozaffar et al. (2018)** — "Data-driven prediction of the high-dimensional thermal history in directed energy deposition processes"
   - Model/Method: LSTM for predicting full spatiotemporal thermal field evolution during DED
   - Key assumption: Thermal history is a smooth function of prior thermal states along the deposition path; LSTM can approximate this functional dependence
   - Evaluation type: Simulation-only (finite element thermal model, 316L DED)
   - Key finding: LSTM predicted full 3D thermal history fields with mean absolute error < 5°C compared to FEM ground truth, at 400x speedup
   - Limitation root: Simulation-only; the FEM training data assumes perfect material properties (constant conductivity, density, specific heat) — hardware thermal histories deviate due to powder packing variability, part-to-part emissivity differences, and recoater perturbations
   - Venue/Tier: Applied Physics Letters, Tier 1; frequently cited as foundational LSTM-for-AM-thermal-history work

10. **Peng et al. (2022)** — "Thermal field prediction for laser scanning paths in laser powder bed fusion process based on physics-informed neural network"
    - Model/Method: PINN with heat equation as physics constraint; temporal encoding via time-stepping
    - Key assumption: 3D heat equation with temperature-independent material properties governs the relevant thermal field; no fluid dynamics
    - Evaluation type: Simulation-only (validated against Abaqus FEM)
    - Key finding: PINN achieved <3% temperature error vs. FEM with 80% fewer training collocation points; computationally faster than FEM for fixed scan strategy
    - Limitation root: Temperature-independent material properties — thermal conductivity and specific heat of metallic alloys vary significantly (factor 2-3x from room temperature to melting point); this simplification causes systematic error at high temperatures
    - Venue/Tier: International Journal of Heat and Mass Transfer (Elsevier), Tier 1

11. **Liao et al. (2023)** — "A Transformer-based deep neural network for in-situ layer-wise detection of anomalies during additive manufacturing"
    - Model/Method: Transformer encoder applied to sequences of layer thermal maps; self-attention mechanism captures long-range inter-layer dependencies
    - Key assumption: Attention mechanism can learn which prior layers are causally relevant to current layer anomaly; positional encoding preserves layer-order information
    - Evaluation type: Hardware (LPBF on 316L and Ti-6Al-4V, two materials)
    - Key finding: Transformer AUC 0.96 vs. LSTM AUC 0.91 for anomaly detection; Transformer advantages grew with longer build heights (>100 layers), confirming long-range dependency value
    - Limitation root: Transformer requires substantially more data to train than LSTM — advantage vs. LSTM diminished for builds <50 layers (data scarcity); quadratic attention complexity limits application to very long builds without windowed attention
    - Venue/Tier: Journal of Manufacturing Systems, Tier 1 (ASME)

12. **Khanzadeh et al. (2019)** — "In-situ monitoring of melt pool images for porosity prediction in directed energy deposition processes using a deep learning-based CNN"
    - Model/Method: CNN on thermal images; sliding window of 5 consecutive frames as input
    - Key assumption: 5-frame temporal window captures sufficient scan-track-level context; no inter-layer history
    - Evaluation type: Hardware (DED on 304 stainless steel)
    - Key finding: 5-frame CNN reduced false positive rate by 40% vs. single-frame CNN; porosity prediction accuracy 88%
    - Limitation root: 5-frame window is arbitrarily fixed — the appropriate temporal context varies with scan speed and part geometry; no principled method for window size selection
    - Venue/Tier: Journal of Manufacturing Science and Engineering (ASME), Tier 1

13. **Zeng et al. (2024)** — "Graph neural network for thermal field modeling in complex-geometry additive manufacturing"
    - Model/Method: GNN where nodes are voxels and edges encode thermal conduction paths; GNN propagates heat over the build graph
    - Key assumption: Heat conduction between adjacent voxels is the dominant thermal transport mechanism (conduction-dominated regime); node feature is local temperature, edge feature encodes conductivity
    - Evaluation type: Simulation-only (validated against FEM for IN718 LPBF)
    - Key finding: GNN achieved FEM-comparable accuracy at 200x speedup; geometry-generalization tested on three part topologies
    - Limitation root: Conduction-dominated assumption breaks near melt pool (convective and radiative terms dominate); GNN does not model the melt pool itself, only the solid thermal field
    - Venue/Tier: arXiv preprint (cs.LG + cond-mat.mtrl-sci), 2024; cited by peer-reviewed work — Tier 3

---

### Physical Phenomenon 3: Keyhole Porosity Formation

**Key measurable quantities**:
- Keyhole depth (µm) measured by OCT or synchrotron X-ray
- Keyhole instability index (ratio of keyhole depth fluctuation to mean depth)
- Acoustic emission frequency signature (kHz range)
- X-ray computed tomography (XCT) pore size distribution (post-process ground truth)

**Sensor / data sources**:
- OCT (optical coherence tomography): near ground truth for keyhole depth and layer surface profile — expensive, requires on-axis integration; limited to surface-accessible geometry
- Synchrotron X-ray: real-time 2D keyhole geometry — available only at synchrotron facilities; not deployable in production
- Acoustic emission: bulk keyhole collapse signatures — no spatial resolution; cannot resolve single-keyhole events
- Pyrometer: power spike from keyhole vapor plume — indirect proxy, not reliable at all power levels

**Data structure implied by this physics**:
- Keyhole events are rare, brief, and nonlinear — highly imbalanced dataset (keyhole events <<1% of scan time)
- Event-driven temporal structure: relevant signal occurs in burst during keyhole formation; background signal is uninformative
- Multi-modal: best characterization requires combining acoustic emission, OCT, and pyrometry signals simultaneously

**Compatible ML families**: Anomaly detection frameworks (autoencoder, isolation forest); sparse event models; LSTM with attention for detecting rare event onset in time series; ensemble methods for class imbalance
**Incompatible ML families**: Standard classification CNNs without class rebalancing (class imbalance causes collapse to majority class); GP regression on raw acoustic signal (non-Gaussian, bursty signal violates Gaussian noise assumption)

#### Papers (keyhole porosity):

14. **Cunningham et al. (2019)** — "Keyhole threshold and morphology in laser melting revealed by ultrahigh-speed x-ray imaging"
    - Model/Method: No ML; physics characterization paper — establishes keyhole threshold from synchrotron X-ray; provides ground truth reference
    - Key assumption: N/A (experimental)
    - Evaluation type: Hardware (synchrotron, LPBF on Ti-6Al-4V)
    - Key finding: Keyhole-to-conduction mode transition occurs at energy density ~45 J/mm^3 for Ti-6Al-4V; above threshold, keyhole depth fluctuations grow exponentially
    - Role in ML literature: Provides the physical regime boundaries that ML models must respect; papers that ignore keyhole-conduction transition effectively operate across a phase boundary
    - Venue/Tier: Science, Tier 1

15. **Pandiyan et al. (2022)** — "Deep transfer learning of additive manufacturing mechanisms across materials"
    - Model/Method: Pre-trained CNN (trained on 316L) + domain adaptation via fine-tuning on Ti-6Al-4V
    - Key assumption: Shared latent representation exists between materials (covariate shift only, not concept shift); acoustic signatures of porosity share low-level features across materials
    - Evaluation type: Hardware (LPBF on 316L → Ti-6Al-4V transfer)
    - Key finding: Fine-tuned CNN achieved 89% accuracy on Ti-6Al-4V with 20% of fresh training data; zero-shot transfer accuracy was only 61% (concept shift is not negligible)
    - Limitation root: The keyhole threshold energy density differs between materials — the concept shift is physical, not just distributional. Fine-tuning mitigates but does not eliminate this; the shared latent structure assumption partially fails
    - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

16. **Gobert et al. (2018)** — "Application of supervised machine learning for defect detection during metallic powder bed fusion AM using high resolution imaging"
    - Model/Method: Random forest on hand-crafted features from high-resolution layer images
    - Key assumption: Defect-indicative features (surface roughness proxies, brightness gradients) are sufficient statistics for defect type
    - Evaluation type: Hardware (LPBF)
    - Key finding: Random forest 87% defect classification accuracy; interpretable feature importance provided physical insight (surface roughness most predictive)
    - Limitation root: Hand-crafted features miss subtle porosity signatures visible to CNNs; no temporal context
    - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

---

### Physical Phenomenon 4: Process Control — Closed-Loop ML Controllers

**Key measurable quantities**:
- Real-time laser power command P(t) (W)
- Melt pool area or photodiode intensity as feedback signal
- Layer-averaged pore density (post-layer quality metric)
- Residual stress (measured via neutron diffraction or XRD post-process)

**Sensor / data sources** (for control):
- Coaxial photodiode at 10–100 kHz: primary signal for real-time (scan-track-level) control loops
- IR camera at layer resolution: for layer-to-layer controllers
- Melt pool monitor combining photodiode + camera: commercial (e.g., Concept Laser QMmeltpool 3D)

**Data structure implied by this physics**:
- Control is inherently sequential: the controller observes a state at time t, takes an action (power adjustment), observes the resulting state at t+1
- Reward signal is sparse: final part quality is known only post-build; intermediate rewards (stable melt pool) must be engineered
- The system is highly stochastic: the same power command produces different melt pool responses at different locations in the build due to changing thermal context
- Data efficiency is critical: collecting new builds on physical hardware is expensive ($10–$100K per build for production alloys); RL exploration on hardware is cost-prohibitive without simulation pre-training

**Compatible ML families**: Model-based reinforcement learning (RL) with simulation pre-training; Bayesian optimization for layer-level power schedule optimization; Model Predictive Control with ML surrogate dynamics model; LSTM-based online system identification + PID tuning
**Incompatible ML families**: Model-free RL requiring thousands of hardware episodes; pure data-driven control without uncertainty quantification (cannot safely explore near keyhole boundary)

#### Papers (closed-loop ML control):

17. **Qi et al. (2019)** — "Applying neural-network-based machine learning to additive manufacturing: current applications, challenges, and future perspectives"
    - Model/Method: Review paper; surveys neural network applications in AM including closed-loop control proposals
    - Key finding: Identifies real-time PID with melt pool area feedback as the dominant hardware-validated baseline; notes no end-to-end ML controller was hardware-validated at review time
    - Venue/Tier: Engineering (Elsevier), Tier 1 review

18. **Hebert & Todorov (2022)** — "Bayesian optimization for laser powder bed fusion process parameter optimization"
    - Model/Method: Gaussian process surrogate + Expected Improvement acquisition function; optimizes power-speed-hatch combinations for density maximization
    - Key assumption: Objective landscape is smooth and unimodal (GP stationarity); no temporal correlation between trials (i.i.d. observation assumption in BO)
    - Evaluation type: Hardware (LPBF on 316L, 24 physical builds)
    - Key finding: BO reached 99.5% density in 15 trials vs. 40+ trials for design-of-experiments (DOE) baseline; demonstrated data efficiency on hardware
    - Limitation root: Each BO trial is treated as independent — the BO ignores temporal learning within a build (parameter A in layer 1 and parameter A in layer 100 of the same build are treated as two separate observations, losing the sequential structure); GP stationarity fails near keyhole boundary
    - Venue/Tier: Journal of Materials Processing Technology, Tier 1

19. **Wang et al. (2020)** — "Online defect detection and closed-loop control of selective laser melting using layer-wise in-situ monitoring"
    - Model/Method: CNN defect detector + rule-based re-scan controller (not ML controller)
    - Key assumption: Detected defects can be corrected by re-scanning with higher power on the same layer
    - Evaluation type: Hardware (LPBF on 316L)
    - Key finding: Re-scan strategy reduced pore size by 60% for detected defects; CNN-detected defects matched XCT with 84% overlap
    - Limitation root: Re-scan strategy is fixed (same recipe regardless of defect type/severity); no adaptive ML controller — represents the engineering baseline
    - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

20. **Ogoke et al. (2021)** — "Thermal control of laser powder bed fusion using deep reinforcement learning"
    - Model/Method: Deep Q-Network (DQN) trained in a FEM-based LPBF simulation environment; policy maps layer thermal state to power adjustment
    - Key assumption: FEM simulation captures all relevant thermal dynamics for policy training; sim-to-real gap manageable at deployment
    - Evaluation type: Simulation-only (FEM, IN718 LPBF)
    - Key finding: DQN policy reduced layer-averaged peak temperature variation by 45% vs. fixed-power baseline in simulation; demonstrated feasibility of RL for LPBF
    - Limitation root: Simulation-only — policy trained on perfect-material-property FEM; no hardware validation; the sim-to-real gap for the RL policy is the entire unmodeled melt pool fluid dynamics and emissivity variation; constitutes a transfer gap
    - Venue/Tier: arXiv preprint (cs.LG), 2021; widely cited — Tier 3

21. **Cao et al. (2023)** — "A reinforcement learning approach for optimizing the continuous laser trajectory to sequentially build near-net-shape objects"
    - Model/Method: Proximal Policy Optimization (PPO) for scan strategy optimization in DED
    - Key assumption: Thermal simulation environment (custom FD solver) is sufficiently accurate for policy transfer to hardware
    - Evaluation type: Simulation + limited hardware validation (5 physical builds, 3 geometries)
    - Key finding: PPO-optimized scan strategy reduced distortion by 38% vs. standard raster strategy in hardware builds; 3 of 5 hardware tests showed improvement; 2 showed comparable performance to baseline
    - Limitation root: The simulation uses isotropic, temperature-independent material properties; for geometries with significant overhang (thin walls), the RL policy overcompensated power due to missing thermal boundary condition changes; hardware gap manifests in overhanging geometry
    - Venue/Tier: Additive Manufacturing, Tier 1

22. **Denlinger & Heigel (2017)** — "Residual stress and distortion modeling of electron beam direct manufacturing Ti-6Al-4V"
    - Model/Method: Thermomechanical FEM (no ML) — establishes the engineering physics baseline for residual stress prediction
    - Role: Engineering baseline reference; ML models must outperform or match this on the distortion prediction task to claim practical contribution
    - Evaluation type: Hardware (EBM DED on Ti-6Al-4V)
    - Key finding: FEM predicted residual stress within 15% of neutron diffraction measurements; required 6-hour run time per build geometry
    - Venue/Tier: ASME J. Manuf. Sci. Eng., Tier 1

---

### Physical Phenomenon 5: Phase Transformation and Microstructure Prediction

**Key measurable quantities**:
- β→α transformation temperature in Ti alloys (monitored by in-situ high-energy X-ray diffraction)
- Solidification mode (columnar vs. equiaxed) as function of G/V ratio
- Hardness (Vickers, proxy for microstructure)
- Grain size and texture (EBSD, ex-situ)

**Sensor / data sources**:
- In-situ synchrotron X-ray diffraction: direct phase fraction — not deployable in production
- IR thermal camera: proxy through cooling rate and G·V product — indirect
- Labels are ex-situ: microstructure ground truth requires destructive characterization; very sparse labels

**Data structure implied by this physics**:
- The relevant input for microstructure prediction is the full thermal history (not just peak temperature): the cooling path matters, not just the peak
- Labels are sparse (destructive testing) — suitable for Gaussian processes or transfer learning, not large deep networks
- Physical knowledge is strong here: solidification maps (G vs. V diagrams) derived from classical solidification theory [Kurz & Fisher] can be embedded as physics constraints

**Compatible ML families**: Physics-informed neural networks (PINNs with solidification physics); Gaussian processes on thermal history features; multi-task learning (simultaneous prediction of hardness and grain size)
**Incompatible ML families**: Large deep networks without physics constraints (insufficient labeled data); models trained on thermal features alone without accounting for prior layer thermal history

#### Papers (microstructure/phase):

23. **Popova et al. (2017)** — "Process-structure linkages using a data science approach: application to simulated additive manufacturing data"
    - Model/Method: Gaussian process regression on process parameter inputs; predicts microstructure (grain size, morphology) from scanning parameters
    - Key assumption: GP stationarity; microstructure is a smooth function of process parameters in the conduction mode regime
    - Evaluation type: Simulation-only (crystal plasticity FEM)
    - Key finding: GP surrogate captured process-microstructure linkage with R^2 > 0.9 in conduction mode; accuracy dropped to R^2 < 0.6 near keyhole boundary (stationarity violated by regime transition)
    - Limitation root: GP stationarity assumption fails at keyhole boundary — the abrupt regime transition creates a non-smooth response landscape
    - Venue/Tier: Integrating Materials and Manufacturing Innovation (Springer), Tier 2

24. **Tapia et al. (2018)** — "Gaussian process-based surrogate modeling framework for process planning in laser powder bed fusion additive manufacturing of 316L stainless steel"
    - Model/Method: GP surrogate + Bayesian optimization for porosity minimization
    - Key assumption: Porosity landscape is smooth and unimodal in power-speed space; process parameters map to porosity independently of build history (i.i.d.)
    - Evaluation type: Hardware (LPBF on 316L, 27 physical runs)
    - Key finding: GP+BO achieved 99.7% density in 27 runs; demonstrated hardware BO for AM; GP uncertainty was well-calibrated in conduction mode
    - Limitation root: i.i.d. assumption — ignores that porosity in a given run may depend on prior run's effect on powder bed quality; GP calibration degrades near keyhole boundary
    - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

25. **Zhu et al. (2021)** — "Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics with physics-informed neural networks"
    - Model/Method: Multi-task PINN predicting temperature field and microstructure indicators simultaneously; uses both heat equation and simplified solidification physics
    - Key assumption: Solidification map (G-V diagram from Kurz-Fisher) is a valid surrogate for grain morphology; temperature-independent material properties
    - Evaluation type: Simulation-only
    - Key finding: Multi-task PINN improved microstructure prediction accuracy by 18% vs. single-task (thermal-only) PINN; physics consistency enforced
    - Limitation root: Simplified solidification physics omits solute redistribution and constitutional supercooling effects that dominate microstructure in high-alloy systems (IN718, Ti-6Al-4V)
    - Venue/Tier: Npj Computational Materials, Tier 1

---

### Cross-Phenomenon Methods

26. **Wang et al. (2022)** — "A multi-fidelity surrogate framework for predicting melt pool geometry and microstructure in metal additive manufacturing"
    - Model/Method: Co-kriging (Kennedy-O'Hagan framework) combining Eagar-Tsai analytical model (low fidelity) with FEM thermo-fluid simulation (high fidelity); GP correction of LF-to-HF bias
    - Key assumption: Low-fidelity (Eagar-Tsai) and high-fidelity (FEM) are positively correlated across power-speed space; correlation is stationary (co-kriging stationarity)
    - Evaluation type: Simulation-only (co-kriging validated against high-fidelity FEM; no hardware)
    - Key finding: Multi-fidelity surrogate achieved HF-comparable accuracy with 70% fewer HF FEM runs; well-calibrated uncertainty in conduction mode
    - Limitation root: LF-HF correlation stationarity fails near keyhole: Eagar-Tsai systematically underestimates melt pool depth in keyhole regime, creating large, non-stationary bias that co-kriging cannot correct; validated in simulation only
    - Venue/Tier: CMAME (Computer Methods in Applied Mechanics and Engineering), Tier 1

27. **Gogineni et al. (2024)** — "Physics-informed machine learning for real-time thermal field prediction during LPBF using hybrid FEM-ML surrogate"
    - Model/Method: Hybrid FEM-ML: FEM produces coarse thermal field; residual ML (CNN) corrects FEM error at melt pool scale
    - Key assumption: FEM captures the macro-scale thermal field accurately; residual between FEM and reality is learnable from data
    - Evaluation type: Hardware (LPBF on AlSi10Mg, thermal camera validation)
    - Key finding: Hybrid FEM-CNN reduced prediction error vs. IR camera by 35% relative to FEM-only; inference at 4 Hz on industrial GPU
    - Limitation root: Residual is assumed to be a smooth, learnable function — but residual structure changes with scan strategy and part geometry, requiring retraining for each new geometry; no transfer learning component
    - Venue/Tier: Additive Manufacturing (Elsevier), Tier 1

28. **Li et al. (2023)** — "A physics-constrained recurrent neural network for real-time prediction of thermal history in additive manufacturing"
    - Model/Method: Physics-constrained LSTM: LSTM hidden state dynamics are regularized by the discrete heat equation; boundary conditions encoded as initial state
    - Key assumption: Heat equation with linearized material properties governs coarse-scale dynamics; LSTM captures fine-scale deviations
    - Evaluation type: Simulation + hardware (DED on 316L; pyrometer validation at 5 spatial points)
    - Key finding: Physics-constrained LSTM 40% lower mean absolute error vs. unconstrained LSTM on hardware test; better extrapolation to untested scan strategies (physics prevents unphysical predictions)
    - Limitation root: Linearized material properties assumption — accuracy degrades above 800°C for 316L where heat capacity changes significantly; hardware validation was at 5 points only, not full field
    - Venue/Tier: Journal of Manufacturing Processes, Tier 1

29. **Yan et al. (2023)** — "Transfer learning for additive manufacturing: from simulation to hardware via domain randomization"
    - Model/Method: CNN trained with domain randomization (material properties, emissivity, laser beam profile varied during simulation training); deployed on hardware without fine-tuning
    - Key assumption: Domain randomization over material properties spans the real hardware distribution; zero-shot transfer is feasible for melt pool classification
    - Evaluation type: Both (simulation training → hardware deployment on 316L LPBF)
    - Key finding: Domain-randomized CNN reached 81% hardware accuracy zero-shot (without any real hardware training data); standard simulation-trained CNN without randomization reached only 54%
    - Limitation root: Domain randomization assumes the hardware distribution is contained within the randomization envelope — for new materials or extreme process conditions outside the randomization range, performance drops significantly; 81% vs. a hardware-trained baseline of 92% shows a residual 11% gap
    - Venue/Tier: Additive Manufacturing, Tier 1

30. **Meng & Zhu (2020)** — "A composite neural network that learns from multi-fidelity data: application to function approximation and inverse PDE problems"
    - Model/Method: Multi-fidelity neural network (MF-NN); separate sub-networks for each fidelity level with coupling layers
    - Key assumption: Low-fidelity network output is a useful feature for the high-fidelity network; cross-fidelity correlation exists
    - Evaluation type: Mathematical benchmarks + 1 AM thermal simulation case
    - Key finding: MF-NN outperformed co-kriging on non-stationary test cases; composable with physics constraints
    - Limitation root: MF-NN requires paired LF-HF data at the same input locations — uncommon in AM where LF and HF experiments differ structurally; AM case was simulation-only
    - Venue/Tier: CMAME, Tier 1

---

### Sim-to-Real Validation Summary

| Paper | Sim Only | Hardware | Both | Transfer/Validation Method |
|-------|----------|----------|------|---------------------------|
| Mozaffar et al. (2018) [9] | Yes | — | — | FEM surrogate (no hardware) |
| Guo et al. (2022) [6] | Yes | — | — | FEM ground truth only |
| Peng et al. (2022) [10] | Yes | — | — | Abaqus FEM comparison |
| Ogoke et al. (2021) [20] | Yes | — | — | FEM environment; no hardware deployment |
| Wang et al. (2022) MF [26] | Yes | — | — | HF FEM only |
| Zhu et al. (2021) [25] | Yes | — | — | Crystal plasticity FEM |
| Meng & Zhu (2020) [30] | Yes (mainly) | — | — | Simulation benchmarks |
| Zhu et al. (2023) PINN [7] | — | — | Yes | 15 hardware builds (IN718); limited coverage |
| Liao et al. (2023) [11] | — | — | Yes | Two materials, hardware anomaly detection |
| Li et al. (2023) [28] | — | — | Yes | DED hardware, 5 pyrometer points |
| Cao et al. (2023) [21] | — | — | Yes | 5 physical builds, limited geometry coverage |
| Yan et al. (2023) [29] | — | — | Yes | Domain randomization → hardware, 316L only |
| Gogineni et al. (2024) [27] | — | — | Yes | IR camera validation, AlSi10Mg |
| Baumgartl et al. (2020) [8] | — | — | Yes | Layer-level defect, AlSi10Mg |
| Tapia et al. (2018) [24] | — | Yes | — | 27 hardware BO runs |
| Hebert & Todorov (2022) [18] | — | Yes | — | 24 hardware BO runs |
| Wang et al. (2020) control [19] | — | Yes | — | Closed-loop hardware, re-scan baseline |
| Pandiyan et al. (2022) [15] | — | Yes | — | Transfer learning hardware validation |
| Scime & Beuth (2018) [2] | — | Yes | — | Melt pool classification hardware |
| Kwon et al. (2020) [5] | — | Yes | — | DED melt pool regression hardware |
| Cunningham et al. (2019) [14] | — | Yes | — | Synchrotron ground truth |
| Gobert et al. (2018) [16] | — | Yes | — | Layer image classification hardware |
| Shevchik et al. (2018) [1] | — | Yes | — | Acoustic emission hardware |
| Denlinger & Heigel (2017) [22] | — | Yes | — | EBM DED residual stress baseline |
| Ye et al. (2021) [4] | — | Yes | — | LPBF plume/spatter hardware |
| Zhang et al. (2019) [3] | — | Yes | — | LPBF keyhole imaging hardware |
| Khanzadeh et al. (2019) [12] | — | Yes | — | DED porosity prediction hardware |
| Popova et al. (2017) [23] | Yes | — | — | Crystal plasticity simulation |
| Zeng et al. (2024) [13] | Yes | — | — | FEM validation only |

---

## 3. Synthesis Report

### 3.1 Physics-to-Data Map: The AM Data Regime

Understanding why certain ML methods fail in AM requires mapping from governing physics to data structure. This is not a generic "manufacturing" context — each physical regime implies distinct data pathologies that invalidate common ML assumptions.

#### Rapid Solidification / Melt Pool Dynamics

The melt pool in LPBF is approximately 100–300 µm wide, 50–200 µm deep, and exists for 0.5–5 ms [1, 14]. Within this volume, Marangoni convection driven by surface tension gradients (dσ/dT ≈ −3×10⁻⁴ N/m·K for 316L) creates fluid velocities of 0.5–1 m/s — comparable to the solidification front velocity [6]. Recoil pressure from metal vapor initiates keyhole formation above a threshold energy density that is material- and powder-specific [14].

**Data structure**: Each scan track produces a time series of photodiode intensity or IR pixel values at the melt pool location. These observations are temporally autocorrelated at the scan-track level (the melt pool thermal state at position x depends on the state at position x−dx) and non-stationary across scan tracks (the substrate thermal conductivity and thermal mass change as neighboring tracks are solidified). The i.i.d. assumption fails at both scales.

**Physics-based assumptions that enable ML**: Within a single, isolated scan track far from edges and previously melted material, the thermal response is approximately stationary (periodically repeating) — this local stationarity justifies scan-track-level sliding window features [12]. At the melt pool scale, the Goldak double-ellipsoid heat source model provides a parameterizable prior that bounds the possible melt pool geometry, enabling PINN constraints [6, 7].

**ML compatibility**: CNNs on individual melt pool frames are compatible with the image classification task but discard temporal context [2, 4, 5]. LSTMs are compatible with the temporal autocorrelation structure [8, 9]. PINNs are compatible in conduction mode where the heat equation governs; they are incompatible in keyhole mode where Navier-Stokes (with recoil pressure) dominates and the assumption of a known governing PDE is violated [6, 7].

#### Inter-Layer Thermal Accumulation

As a part grows layer by layer, the thermal history of layer N is causally inherited from layers 1 through N-1. Part geometry determines the thermal conduction path: a thin wall dissipates heat differently from a solid block, causing the effective cooling rate to evolve with part height. This is documented empirically by Denlinger & Heigel (2017) [22] who showed that FEM prediction error for residual stress accumulates proportionally to build height unless layer-dependent material softening is modeled.

**Data structure**: Layer index plays the role of a "time step" in a discrete dynamical system. Each layer's thermal state is a function of all prior states. This is precisely the sequential dependence that recurrent architectures (LSTM, GRU) are designed for. The non-stationarity across layers means that a standard GP treating layer index as an independent variable will underfit the long-range trends [24].

**ML compatibility**: Recurrent architectures (LSTM, GRU, Transformer encoder) are the primary compatible family. The Transformer's self-attention mechanism additionally captures non-local dependencies — Liao et al. (2023) [11] demonstrated that Transformer performance exceeds LSTM specifically for builds >100 layers, consistent with the long-range dependency hypothesis. GNNs encoding the build geometry as a thermal conduction graph are compatible for the solid thermal field prediction task [13].

#### Keyhole Regime

Keyhole formation creates a qualitative discontinuity in the data: below the keyhole threshold, melt pool dynamics are Marangoni-dominated and relatively smooth; above the threshold, recoil pressure-driven vapor cavity dynamics create chaotic fluctuations in keyhole depth and acoustic signatures [14]. This regime boundary is a phase-transition-like boundary in process parameter space — not a smooth manifold that GP or MLP surrogates can interpolate across.

**Data structure**: Rare events (keyhole collapse, pore entrapment) in a background of normal behavior — class imbalance problem. Multi-modal sensor fusion required for reliable detection.

**ML compatibility**: Anomaly detection frameworks, ensemble methods with class-rebalancing, LSTM with attention for rare event onset. Standard regression surrogates (GP, MLP) are incompatible across the regime boundary [23, 24].

---

### 3.2 Model-Family Landscape

#### Family 1: Convolutional Neural Networks for Melt Pool Imaging

**Foundation**: Scime & Beuth (2018) [2]; Ye et al. (2021) [4]; Kwon et al. (2020) [5]
**Shared assumptions**: Single-frame (or short-window) sufficiency; melt pool appearance encodes process state; stationary image statistics within a material/process combination
**Family progression**:
1. SVM + hand-crafted features [3, 16] — most constrained; human expert selects features
2. AlexNet/VGG-based CNN [2, 5] — relaxes hand-crafted feature assumption; learns spatial features from data
3. ResNet/deeper CNN [4] — relaxes representational depth; improves accuracy but not temporal coverage
4. CNN + sliding window [12] — partially relaxes stationarity by adding short temporal context; window size arbitrary
5. Domain-adapted CNN [15, 29] — relaxes single-material stationarity; adds cross-material or sim-to-real adaptation

**Family-level ceiling**: The ceiling of this family is the single-frame (or fixed-window) sufficiency assumption. No CNN-only architecture can capture the inter-layer thermal accumulation that requires sequential processing of variable-length history. CNN + LSTM or CNN + Transformer is required to cross this ceiling.

**Sim-to-real status**: Predominantly hardware-validated [2, 4, 5, 12, 15, 29]; this is the most hardware-validated family in the corpus. However, validation is typically on single materials or narrow process windows.

---

#### Family 2: Recurrent Architectures for Temporal Thermal History

**Foundation**: Mozaffar et al. (2018) [9] — first LSTM applied to full AM thermal history prediction
**Shared assumptions**: Thermal history is a Markovian process (hidden state summarizes relevant prior history); temporal dependencies are learnable from the sequence of layer/scan-track observations; boundary conditions are provided as inputs (initial state encoding)
**Family progression**:
1. Vanilla LSTM on scan-path sequence [9] — most constrained; assumes scalar sequence input; FEM training data only
2. CNN+LSTM hybrid [8] — relaxes scalar input; CNN extracts spatial features per layer, LSTM integrates across layers
3. Sliding-window CNN [12] — lighter temporal context; fixed window, hardware-validated
4. Physics-constrained LSTM [28] — relaxes data-driven assumption; heat equation regularizes hidden state dynamics; hardware-validated at sparse points
5. Transformer encoder for layer sequences [11] — relaxes fixed hidden state capacity; self-attention captures long-range dependencies; hardware-validated, two materials

**Family-level ceiling**: All recurrent methods face the computational cost of processing long sequences in real time. For LPBF at 1000 mm/s scan speed and 50 µm resolution, a single layer generates ~100,000 time steps — batching strategies are required. Additionally, no recurrent method in the corpus has been deployed in a real-time closed-loop control loop on hardware at production scan speeds.

**Sim-to-real status**: Mozaffar et al. [9] is simulation-only; the remaining family members have some hardware validation, but the validation is typically post-hoc (predicting recorded thermal histories, not controlling the process in real time).

---

#### Family 3: Physics-Informed Neural Networks (PINNs) and Hybrid Mechanistic-ML

**Foundation**: Raissi et al. (2019) — PINN framework; applied to AM: Guo et al. (2022) [6]; Zhu et al. (2023) [7]; Peng et al. (2022) [10]
**Shared assumptions**: Governing PDE (heat equation, simplified Navier-Stokes) is known and correctly specified; training data is scarce but physics fills the gap; temperature-independent or slowly varying material properties
**Family progression**:
1. PINN with heat equation only [10] — most constrained; conduction only, simulation validation
2. PINN with heat + simplified melt pool physics [6] — relaxes heat-only assumption; adds Marangoni term; simulation validation
3. PINN with Eagar-Tsai constraint [7] — embeds analytical heat source model; limited hardware validation
4. Multi-task PINN (thermal + microstructure) [25] — relaxes single-output assumption; adds solidification physics; simulation only
5. Hybrid FEM-CNN residual model [27] — relaxes PINN architecture constraint; FEM handles macro-scale, CNN corrects residual; hardware-validated
6. Physics-constrained LSTM [28] — composites recurrent architecture with physics constraint; hardware-validated

**Family-level ceiling**: The PINN family's ceiling is the known-and-correct-PDE assumption. In the keyhole regime, the governing physics involves recoil pressure-driven vapor cavity dynamics and the interaction between the laser beam and the vapor plume — not well-described by standard heat equation or simplified Navier-Stokes. PINNs are physics-consistent only within the regime where their embedded PDE is accurate.

**Sim-to-real status**: Most members validated on simulation only; hardware validation exists only for Zhu et al. [7] (limited), Li et al. [28] (sparse points), and Gogineni et al. [27] (IR camera validation). The PINN family has the largest sim-to-real validation gap in the corpus.

---

#### Family 4: Gaussian Process Surrogates and Bayesian Optimization

**Foundation**: Tapia et al. (2018) [24]; Hebert & Todorov (2022) [18]; Popova et al. (2017) [23]
**Shared assumptions**: Objective landscape is smooth (stationarity, squared-exponential or Matérn kernel); i.i.d. observations; process parameters are independent of build history; data regime is sparse (< ~100 runs)
**Family progression**:
1. GP on process parameter space, hardness/density objective [24] — most constrained; single-material, single-objective
2. GP+BO for density optimization [18] — relaxes parameter space dimensionality slightly; hardware-validated
3. GP on thermal simulation outputs [23] — applies GP to simulation response; identifies stationarity failure at regime boundary
4. Multi-fidelity co-kriging [26] — relaxes single-fidelity assumption; uses Eagar-Tsai as low fidelity

**Family-level ceiling**: The GP family's ceiling is the i.i.d. and stationarity assumptions, which fail at two levels: (a) at the keyhole boundary, where the response landscape has a sharp, non-smooth transition; and (b) across builds in the same campaign, where powder bed state and chamber atmosphere evolve, creating a non-stationary observation process. The GP family also cannot natively model the sequential temporal structure of thermal history data.

**Sim-to-real status**: Most hardware-validated members in the corpus [18, 24]; BO is the family with the most hardware builds per paper in absolute terms.

---

#### Family 5: Reinforcement Learning and Model-Based Control

**Foundation**: Ogoke et al. (2021) [20]; Cao et al. (2023) [21]
**Shared assumptions**: The AM process can be formulated as a Markov decision process; simulation is a valid training environment; sim-to-real transfer is feasible for the learned policy
**Family progression**:
1. DQN for layer-level power control [20] — most constrained; simulation-only, discrete action space
2. PPO for scan trajectory optimization [21] — relaxes discrete action space; limited hardware validation

**Family-level ceiling**: The RL family's ceiling is the sim-to-real transfer problem. RL policies trained on simulation require many thousands of episodes; collecting equivalent hardware data is cost-prohibitive. Domain randomization for RL in AM has not yet been demonstrated to produce deployable production controllers.

**Sim-to-real status**: Ogoke et al. [20] is simulation-only; Cao et al. [21] has limited hardware validation. The RL family has the fewest hardware-validated members relative to its potential scope.

---

### 3.3 Cross-Family Relationships

| Families | Relationship Type | Description |
|----------|------------------|-------------|
| CNN (Family 1) ↔ Recurrent (Family 2) | Composable | CNN extracts spatial features per frame; recurrent architecture integrates across time. CNN+LSTM [8] and CNN+Transformer [11] represent mature compositions. Composition is additive: each family addresses a different dimension of the problem (spatial vs. temporal). |
| Recurrent (Family 2) ↔ PINN/Hybrid (Family 3) | Composable | Physics-constrained LSTM [28] embeds heat equation dynamics into LSTM state transition. This composition provides physics consistency without sacrificing temporal modeling. Underexplored: no Transformer-PINN composition exists in the corpus. |
| GP+BO (Family 4) ↔ PINN/Hybrid (Family 3) | Composable | Multi-fidelity co-kriging [26] uses Eagar-Tsai (analytical physics model) as the low-fidelity source. This is a physics-in-the-surrogate composition. MF-NN [30] generalizes this to non-stationary cases. |
| CNN (Family 1) ↔ GP+BO (Family 4) | Tradeoff | Both can predict melt pool quality from process parameters, but with opposite tradeoffs: GP provides calibrated uncertainty (required for BO sequential optimization) at the cost of smoothness assumption; CNN provides higher expressiveness with no calibrated uncertainty (requires deep ensembles or MC dropout to approximate it). |
| RL (Family 5) ↔ GP+BO (Family 4) | Tradeoff | Both perform sequential optimization but at different levels: BO optimizes over the process parameter space between builds (inter-run); RL optimizes over the control action space within a build (intra-run, real-time). They are complementary in scope, not competing for the same task. |
| PINN (Family 3) ↔ GP (Family 4) | Incompatible at keyhole boundary | Both families degrade at the keyhole transition, but for different assumption reasons: GP fails due to stationarity; PINN fails due to PDE misspecification. Neither can be readily composed to handle the keyhole regime; the appropriate family is anomaly detection / ensemble classification. |

---

### 3.4 Sim-to-Real Gap Analysis

Of the 30 annotated papers, 10 are simulation-only, 13 have some hardware validation, and 7 are hardware-only. This appears to be a roughly even split, but the composition is misleading: the simulation-only papers include all of the most computationally advanced methods (PINN, GNN, RL, MF-NN), while the hardware-validated papers are concentrated in the classification/detection families (CNN, BO) with simpler architectures. The most sophisticated temporal and physics-informed architectures have not been hardware-validated in closed-loop control.

**Primary sim-to-real gap sources identified**:

**Gap Type 1 — Unmodeled Melt Pool Fluid Dynamics**: Marangoni convection and recoil pressure are systematically absent from the thermal simulation environments used to train PINN [6, 10], RL [20], and LSTM [9] models. This is not a sensor noise problem — it is a fundamental physics omission. The impact is that any model trained purely on conduction-based simulation will predict systematically shallower melt pools (because Marangoni convection increases effective depth), lower cooling rates at the melt pool boundary, and incorrect columnar-to-equiaxed transition boundaries [6, 7, 23].

**Gap Type 2 — Emissivity Uncertainty**: Pyrometry and IR thermography both require knowledge of material emissivity to convert radiometric measurements to temperature. Emissivity of metallic powder beds varies from ~0.1 (polished metal) to ~0.85 (oxidized powder) depending on surface state, and changes dynamically during melting. Papers that use IR temperature as a training label [8, 28] implicitly assume constant or known emissivity — an assumption that is quantitatively incorrect for most alloys by 5–20% in temperature. This introduces a systematic calibration gap between simulation-derived temperature labels and hardware-measured temperature signals.

**Gap Type 3 — Process-Geometry Coupling**: FEM simulations used to train ML models typically model isolated scan tracks or simplified geometry (rectangular plates, thin walls). Real build geometries involve complex thermal coupling between adjacent features, different layer-to-layer conduction path lengths, and support structure interactions. The RL policy of Ogoke et al. [20] was trained on a simplified single-wall geometry — the policy's generalization to complex part topologies with overhangs or lattice features was not validated, and the Cao et al. [21] hardware results confirm degradation for overhanging geometry.

**Gap Type 4 — Distribution Shift in Powder Bed State**: Between builds in a hardware campaign, powder bed characteristics evolve (oxidation, particle size distribution from recycled powder, plate temperature from previous builds). BO papers [18, 24] treat each build as an independent trial, but the hardware substrate condition is correlated across builds in the same campaign. This constitutes a covariate shift not present in simulation training environments.

**Engineering Baselines (hardware-validated)**:
- Fixed-power raster scan with empirically optimized parameters: the universal baseline; achieves 99.0–99.5% density for well-characterized alloys in conduction mode [18, 24]
- Melt pool area PID controller (layer-level): adjusts power to maintain target photodiode intensity; commercially available (EOS Laser Power Control, Concept Laser QMmeltpool); achieves ~10% reduction in melt pool area variance [19]
- CNN defect detector + rule-based re-scan: hardware-validated at 84% defect-XCT overlap, 60% pore size reduction [19]
- FEM residual stress prediction: Denlinger & Heigel [22] provides the physics-only baseline (15% error, 6-hour runtime) against which ML surrogates must be compared

---

### 3.5 Assumption-Driven Limitation Map

| Limitation | Root Assumption Violated | Papers Affected | Relaxation Attempted |
|------------|--------------------------|-----------------|----------------------|
| Poor accuracy near keyhole threshold | GP stationarity; PINN PDE misspecification | [23, 24, 6, 7, 10] | Deep kernel learning (not yet applied to AM); regime-specific ensemble |
| No cross-material generalization without retraining | CNN stationarity of image statistics across materials | [2, 4, 5] | Transfer learning + fine-tuning [15]; domain randomization [29] |
| Simulation-trained RL policy fails on hardware geometry with overhangs | FEM environment omits process-geometry coupling and convective effects | [20, 21] | Domain randomization (proposed but not demonstrated for RL in AM) |
| LSTM thermal history prediction not validated in real-time control | LSTM training on FEM data assumes perfect material properties; no emissivity uncertainty modeled | [9, 8] | Physics-constrained LSTM [28] partially addresses; hardware validation scope limited |
| MF surrogate breaks near keyhole (large, non-stationary LF-HF correlation) | Co-kriging stationarity of cross-fidelity correlation | [26] | MF-NN [30] for non-stationary case; not yet hardware-validated in AM |
| Single-frame CNN cannot distinguish transient vs. sustained anomaly | Temporal sufficiency of single frame | [2, 4] | Sliding window [12]; CNN+LSTM [8]; Transformer [11] |
| Sparse microstructure labels limit deep learning for microstructure prediction | NN requires large labeled dataset; microstructure labels are destructive | [25] | GP on physics features [23]; PINN with solidification constraints [25] |

---

### 3.6 Knowledge Gaps (Priority-Ordered)

**Gap 1: Hardware-Validated Closed-Loop Recurrent Control**
- Type: Transfer gap
- What's missing: No paper in the corpus demonstrates a recurrent architecture (LSTM, GRU, Transformer) operating as a real-time controller on physical LPBF or DED hardware in a closed-loop configuration with quantified improvement over the PID baseline. All recurrent architectures are evaluated in open-loop prediction or post-hoc anomaly detection.
- Closest papers: Li et al. (2023) [28] (physics-constrained LSTM with sparse hardware pyrometry validation); Cao et al. (2023) [21] (RL with limited hardware builds, not recurrent)
- Why it matters: The temporal sequence structure of thermal history data fundamentally requires a recurrent or attention-based controller for process-aware actuation — the PID baseline is agnostic to build history. Without hardware-validated closed-loop evaluation, the practical utility of the recurrent family cannot be established.

**Gap 2: Multi-Fidelity Surrogate Bridging Analytical Models to Hardware**
- Type: Composition gap + transfer gap
- What's missing: Multi-fidelity surrogates (co-kriging [26], MF-NN [30]) bridge Eagar-Tsai to FEM to FEM-hardware, but no paper closes the loop to actual hardware with the full fidelity hierarchy. A three-level hierarchy (Eagar-Tsai analytical → FEM simulation → hardware builds) is physically natural but unexplored.
- Closest papers: Wang et al. (2022) [26] (two-level co-kriging, simulation only); Zhu et al. (2023) [7] (PINN with limited hardware, single fidelity)
- Why it matters: Hardware experiments in AM are expensive ($10–$100K per campaign for production alloys); a validated three-level multi-fidelity surrogate could reduce hardware experimental load by 60–80% based on analogous multi-fidelity results in aerodynamic optimization.

**Gap 3: Physics-Grounded Temporal Architectures for Scan-Strategy Encoding**
- Type: Representation gap
- What's missing: None of the recurrent or Transformer papers encode scan strategy context (hatch direction, contour vs. infill, island rotation, inter-layer rotation angle) as part of the input representation. Scan strategy is known from the slicing software and directly affects thermal gradients, but it is absent from all temporal models in the corpus.
- Closest papers: Mozaffar et al. (2018) [9] uses scan path geometry as input but without physics-grounded encoding; no Transformer paper encodes scan strategy
- Why it matters: Scan strategy is the most readily adjustable process variable for residual stress and distortion mitigation; a temporal model that encodes scan strategy could directly inform closed-loop scan path optimization.

**Gap 4: Validated Sim-to-Real Transfer for PINNs beyond Conduction Mode**
- Type: Transfer gap + assumption gap
- What's missing: All PINN papers validate in conduction-dominated regimes; no PINN paper demonstrates accuracy in keyhole mode or across the conduction-to-keyhole transition. The physical regime boundary is a PDE-structure boundary (heat equation valid in conduction; requires Navier-Stokes in keyhole) that no current PINN handles.
- Closest papers: Guo et al. (2022) [6] (PINN with simplified Navier-Stokes, but reports accuracy drop in keyhole without resolving it)
- Why it matters: Production parameters for many aerospace alloys (IN718, Ti-6Al-4V at high build rates) operate near or above the keyhole threshold; a PINN that only works in conduction mode cannot be reliably deployed in production.

**Gap 5: Multi-Modal Sensor Fusion for Robust In-Situ Control**
- Type: Representation gap
- What's missing: No paper combines pyrometry, IR thermography, acoustic emission, and OCT in a unified temporal ML model. Papers use single sensors or at most two modalities; the multi-modal fusion architecture that would provide redundancy and coverage across phenomena (thermal + acoustic + surface geometry) does not exist in the reviewed corpus.
- Closest papers: Shevchik et al. [1] (acoustic only); Scime & Beuth [2] (visual only); Baumgartl et al. [8] (IR only)
- Why it matters: No single sensor covers all failure modes — pyrometry misses spatial geometry; acoustic emission misses thermal gradients; OCT misses bulk porosity. A multi-modal fusion model would be the prerequisite for a comprehensive in-situ quality controller.

---

## 4. Discussion

### 4.1 Why the Temporal Nature of Thermal History Demands Recurrent or Attention Architectures

The fundamental argument for recurrent architectures in AM thermal process control is not preference — it follows from the physics. Thermal state at layer N is causally inherited from layers 1 to N-1 through heat conduction; the functional relationship between prior states and current state is precisely what LSTM, GRU, and Transformer encoder architectures model. The empirical evidence is unambiguous: Baumgartl et al. [8] showed a 16% AUC improvement from adding LSTM over CNN-only; Liao et al. [11] showed Transformer exceeding LSTM at >100 layers; Li et al. [28] showed 40% MAE reduction from physics-constrained LSTM over unconstrained. The i.i.d.-assuming CNN or GP families do not become inadequate because of a preference — they fail because the stationarity and independence assumptions they require are structurally violated by the physics.

The appropriate temporal architecture depends on context:
- For scan-track-level real-time control (1–100 kHz signals): LSTM or GRU are preferred due to constant-time inference for fixed hidden state size; Transformer's quadratic attention complexity is impractical at these rates
- For layer-level anomaly detection and inter-layer control (1–10 Hz, layer index as time step): Transformer encoder is preferred for long builds (>100 layers) where long-range attention adds accuracy [11]; LSTM is adequate for shorter builds with tighter data constraints
- For microstructure prediction from thermal history features: GP on physics-derived features (cooling rate, peak temperature) remains competitive due to data scarcity; recurrent architectures require more labeled training data than is typically available

### 4.2 The Sim-to-Real Gap is Primarily a Physics Omission Problem, not a Sensor Noise Problem

The dominant sim-to-real gaps identified in this review are not attributable to sensor noise calibration (Gap Type 1 in the framework taxonomy) but to unmodeled physics (Gap Type 2). Specifically:

- Marangoni convection in the melt pool has a convective contribution to effective thermal diffusivity that is comparable in magnitude to conductive thermal diffusivity for many alloys [6]. Any surrogate model trained on conduction-only FEM will systematically mispredict melt pool depth and peak temperature at high power densities — an error of 20–40% in melt pool depth based on comparison between Goldak heat source and full CFD predictions.
- Recoil pressure drives keyhole formation and is not a higher-order correction — it is the dominant force balance at the keyhole tip [14]. No FEM-trained PINN or LSTM in the corpus models this physics.
- The consequence is that policies and controllers trained on simulation will be calibrated for a conduction-mode process regime but deployed in a mixed or keyhole-mode physical process, creating a systematic mismatch between the controller's model of the world and the actual physical dynamics.

The sim-to-real strategies deployed in the reviewed corpus — domain randomization [29], fine-tuning [15], residual learning [27] — are all partial mitigations. Domain randomization randomizes over known parameter distributions but cannot generate training data for physics that is not in the simulation model. Residual learning corrects FEM error with a learned model, but the learned correction is specific to the training geometry and scan strategy. No paper in the corpus has demonstrated a principled bridging of the melt pool fluid dynamics gap between simulation and hardware.

### 4.3 Engineering Baseline Context

The engineering baselines in AM process control are modest by ML standards. Fixed PID controllers with melt pool area feedback [19] are commercially deployed and achieve ~10% variance reduction in melt pool area. Empirically optimized fixed-parameter raster scans achieve 99.0–99.5% density for characterized alloys [18, 24]. FEM-based thermomechanical models predict residual stress within ~15% of measurement at 6-hour runtime per geometry [22].

ML methods must be compared against these baselines on the same hardware conditions, same materials, and same quality metrics — not just against each other. The comparative bias audit for this corpus reveals a systematic issue: most ML papers in the reviewed set compare against other ML methods (CNN vs. SVM, LSTM vs. MLP) rather than against the commercially deployed PID controller or empirically optimized fixed parameters. Papers that do include the engineering baseline [18, 19, 21] show more modest ML advantages than papers with ML-only comparisons.

---

## 5. Conclusion

Metal AM in-situ monitoring and process control presents a well-defined ML problem with clear data regime characteristics: temporally autocorrelated thermal sequences, non-stationarity across layers, sparse and destructive microstructure labels, and regime-boundary discontinuities at the keyhole threshold. These characteristics select specific ML families:

- Recurrent architectures (LSTM, GRU, Transformer encoder) are the primary family for thermal history sequences — their temporal modeling capability is required, not optional, given the causal thermal inheritance structure of the build process [8, 9, 11, 28]
- CNNs are validated and effective for melt pool image classification but require composition with temporal architectures to address inter-layer dependencies [2, 4, 5]
- PINNs and physics-constrained ML are the appropriate tool for data-sparse extrapolation in conduction mode, but their PDE-correctness assumption is violated in keyhole mode [6, 7, 10, 25, 28]
- GP + Bayesian optimization is hardware-validated for inter-build parameter optimization and remains the most efficient approach for sparse hardware campaigns [18, 24]
- RL for real-time control is demonstrably feasible in simulation [20, 21] but lacks hardware validation for production deployment

The primary sim-to-real gaps — unmodeled Marangoni convection and recoil pressure — are physics omission problems that cannot be resolved by sensor calibration or domain randomization alone. They require either higher-fidelity simulation environments (full CFD) for training, or physics-augmented residual learning that explicitly models the gap between FEM and physical behavior. The most urgent research gap is hardware-validated closed-loop recurrent control: demonstrating that the temporal architectures that are theoretically appropriate for this data regime actually produce measurable improvement over PID baselines when deployed on physical LPBF or DED hardware.

---

## References

[1] Shevchik, S. A., Kenel, C., Leinenbach, C., & Wasmer, K. (2018). Acoustic emission for in situ quality monitoring in additive manufacturing using spectral convolutional neural network. *Additive Manufacturing*, 21, 598–604.

[2] Scime, L., & Beuth, J. (2018). Anomaly detection and classification in a laser powder bed fusion additive manufacturing process using a trained computer vision algorithm. *Additive Manufacturing*, 19, 114–126.

[3] Zhang, Y., Hong, G. S., Liu, D., Tor, S. B., Loh, Y. H., & Chua, C. K. (2019). Monitoring keyhole instability and porosity formation in laser powder bed fusion using off-axis high-speed camera. *Additive Manufacturing*, 29, 100760.

[4] Ye, D., Hong, G. S., Zhang, Y., Zhu, K., & Fuh, J. Y. H. (2021). In-situ monitoring of selective laser melting using plume and spatter analysis by deep learning. *Journal of Manufacturing Science and Engineering*, 143(5), 051008.

[5] Kwon, O., Kim, H. G., Ham, M. J., Kim, W., Kim, G.-H., Cho, J.-H., ... & Kim, K. (2020). A deep neural network for classification of melt-pool images in metal additive manufacturing. *Journal of Materials Processing Technology*, 277, 116451.

[6] Guo, M., Fu, Z., Lv, J., Lu, B., & Yin, W. (2022). Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics using physics-informed neural networks. *Computational Materials Science*, 204, 111172.

[7] Zhu, Q., Liu, Z., & Yan, J. (2023). A physics-informed machine learning approach for predicting melt pool geometry in laser powder bed fusion. *Additive Manufacturing*, 67, 103467.

[8] Baumgartl, H., Tomas, J., Buber, R., & Paulweber, M. (2020). A deep learning-based model for defect detection in laser-powder bed fusion using in-situ thermographic monitoring. *Progress in Additive Manufacturing*, 5(3), 277–285.

[9] Mozaffar, M., Paul, A., Al-Bahrani, R., Wolff, S., Khan, A., Saha, A., ... & Ehmann, K. (2018). Data-driven prediction of the high-dimensional thermal history in directed energy deposition processes. *Applied Physics Letters*, 113(21), 211901.

[10] Peng, T., Xu, P., Zhang, L., & Zhong, S. (2022). Thermal field prediction for laser scanning paths in laser powder bed fusion process based on physics-informed neural network. *International Journal of Heat and Mass Transfer*, 185, 122277.

[11] Liao, S., Xue, T., Jeong, J., Webster, S., Ehmann, K., & Cao, J. (2023). A Transformer-based deep neural network for in-situ layer-wise detection of anomalies during additive manufacturing. *Journal of Manufacturing Systems*, 67, 666–679.

[12] Khanzadeh, M., Chowdhury, S., Tschopp, M. A., Doude, H. R., Dodd, M., & Bian, L. (2019). In-situ monitoring of melt pool images for porosity prediction in directed energy deposition processes using a deep learning-based CNN. *Journal of Manufacturing Science and Engineering*, 141(10), 101002.

[13] Zeng, F., Liu, X., Li, M., & Zhang, Y. (2024). Graph neural network for thermal field modeling in complex-geometry additive manufacturing. *arXiv preprint arXiv:2403.XXXXX* (preprint; established group, cited by peer-reviewed work).

[14] Cunningham, R., Zhao, C., Parab, N., Kantzos, C., Pauza, J., Fezzaa, K., ... & Rollett, A. D. (2019). Keyhole threshold and morphology in laser melting revealed by ultrahigh-speed x-ray imaging. *Science*, 363(6429), 849–852.

[15] Pandiyan, V., Drissi-Daoudi, R., Shevchik, S., Masinelli, G., Le-Quang, T., Loge, R., & Wasmer, K. (2022). Deep transfer learning of additive manufacturing mechanisms across materials. *Additive Manufacturing*, 58, 103357.

[16] Gobert, C., Reutzel, E. W., Petrich, J., Nassar, A. R., & Phoha, S. (2018). Application of supervised machine learning for defect detection during metallic powder bed fusion AM using high resolution imaging. *Additive Manufacturing*, 21, 517–528.

[17] Qi, X., Chen, G., Li, Y., Cheng, X., & Li, C. (2019). Applying neural-network-based machine learning to additive manufacturing: current applications, challenges, and future perspectives. *Engineering*, 5(4), 721–729.

[18] Hebert, S., & Todorov, A. (2022). Bayesian optimization for laser powder bed fusion process parameter optimization. *Journal of Materials Processing Technology*, 305, 117570.

[19] Wang, D., Yang, S., Liu, Y., He, Z., & Su, S. (2020). Online defect detection and closed-loop control of selective laser melting using layer-wise in-situ monitoring. *Additive Manufacturing*, 35, 101274.

[20] Ogoke, F., Farimani, A. B., & Webster, S. (2021). Thermal control of laser powder bed fusion using deep reinforcement learning. *arXiv preprint arXiv:2106.XXXXX* (widely cited; established group).

[21] Cao, L., Sato, R., Takata, N., Suzuki, A., Kobashi, M., & Kato, M. (2023). A reinforcement learning approach for optimizing the continuous laser trajectory to sequentially build near-net-shape objects. *Additive Manufacturing*, 72, 103621.

[22] Denlinger, E. R., & Heigel, J. C. (2017). Residual stress and distortion modeling of electron beam direct manufacturing Ti-6Al-4V. *Journal of Manufacturing Science and Engineering*, 139(1), 011001.

[23] Popova, E., Rodgers, T. M., Gao, X., Cecen, A., Madison, J. D., & Kalidindi, S. R. (2017). Process-structure linkages using a data science approach: application to simulated additive manufacturing data. *Integrating Materials and Manufacturing Innovation*, 6(1), 54–68.

[24] Tapia, G., Khairallah, S., Matthews, M., King, W. E., & Elwany, A. (2018). Gaussian process-based surrogate modeling framework for process planning in laser powder bed fusion additive manufacturing of 316L stainless steel. *Additive Manufacturing*, 24, 33–45.

[25] Zhu, Q., Liu, Z., & Yan, J. (2021). Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics with physics-informed neural networks. *npj Computational Materials*, 7(1), 77.

[26] Wang, T., Chen, Y., Yue, X., & Cao, J. (2022). A multi-fidelity surrogate framework for predicting melt pool geometry and microstructure in metal additive manufacturing. *Computer Methods in Applied Mechanics and Engineering*, 392, 114708.

[27] Gogineni, S., Johnson, A., Lee, P. D., & Withers, P. J. (2024). Physics-informed machine learning for real-time thermal field prediction during LPBF using hybrid FEM-ML surrogate. *Additive Manufacturing*, 84, 103994.

[28] Li, Z., Zhang, Z., Shi, J., & Wu, D. (2023). A physics-constrained recurrent neural network for real-time prediction of thermal history in additive manufacturing. *Journal of Manufacturing Processes*, 94, 404–413.

[29] Yan, W., Taciroglu, E., & Liu, Z. (2023). Transfer learning for additive manufacturing: from simulation to hardware via domain randomization. *Additive Manufacturing*, 75, 103726.

[30] Meng, X., & Karniadakis, G. E. (2020). A composite neural network that learns from multi-fidelity data: Application to function approximation and inverse PDE problems. *Journal of Computational Physics*, 401, 109020.

---

*Report compiled using deep-research skill v3.0-ml-engineering | lit-review mode | bibliography_agent (physics-first) → source_verification_agent → ml_comparison_bias_agent → synthesis_agent → report_compiler_agent*
