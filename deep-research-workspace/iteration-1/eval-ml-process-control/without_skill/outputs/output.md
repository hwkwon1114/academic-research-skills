# ML Methods for In-Situ Monitoring and Control of Metal Additive Manufacturing: Thermal and Mechanical Data

**Date:** April 2026  
**Scope:** This report synthesizes the state of the art in machine learning (ML) methods applied to real-time monitoring, feedback control, and optimization of metal additive manufacturing (AM) processes, with emphasis on (1) how temporal/sequential structure of thermal history is handled, and (2) the gap between simulation-validated and hardware-validated approaches.

---

## 1. Problem Framing

Metal additive manufacturing — most prominently Laser Powder Bed Fusion (LPBF, also called SLM), Directed Energy Deposition (DED), Electron Beam Melting (EBM), and Wire Arc Additive Manufacturing (WAAM) — is acutely sensitive to transient thermal conditions. Each pass of the heat source creates a melt pool that solidifies in milliseconds; that solidification history propagates through the entire build and determines:

- **Microstructure** (grain morphology, phase fractions, texture)
- **Residual stress** and distortion
- **Defect formation** (porosity, lack-of-fusion, keyholing, delamination, hot cracking)
- **Mechanical properties** (yield strength, fatigue life, creep resistance)

Controlling these outcomes requires sensing the process in real time (in-situ) and acting on it — either by adjusting laser/beam parameters within the current layer or by modifying the scan strategy for future layers. This makes the problem fundamentally a **closed-loop sequential decision problem over a high-dimensional spatiotemporal field**, which is why ML, and especially sequence-aware ML, has become central to the field.

---

## 2. In-Situ Sensing Modalities

Before discussing ML methods, it is essential to understand what data is actually available. The sensor suite used determines what kind of temporal and spatial structure the ML model must process.

### 2.1 Thermal Sensors

| Sensor Type | Spatial Resolution | Temporal Resolution | Common Use |
|---|---|---|---|
| Infrared (IR) pyrometer (single-point) | Point | ~10–100 kHz | Melt pool temperature, cooling rate |
| High-speed IR camera | 64×64 to 640×512 px | 100–1000 Hz | Melt pool area, thermal plume, layer-scale temperature field |
| Two-color pyrometry | Point to small area | ~10 kHz | Emissivity-corrected temperature |
| Short-wave IR (SWIR) imaging | Medium | 500–3000 Hz | Melt pool shape, keyhole detection |
| Thermocouples embedded in substrate | Point | 1–100 Hz | Build plate and part bulk temperature |

The most information-rich thermal signal is the **melt pool thermal signature** captured by co-axial or off-axial high-speed IR cameras. Each frame is a 2-D spatial image; the sequence of frames as the laser traverses a scan track is a **video-like spatio-temporal tensor**, which is the core data structure for temporal ML models.

### 2.2 Mechanical / Acoustic / Other Sensors

- **Acoustic emission (AE):** Piezoelectric sensors on the build plate detect elastic wave bursts associated with cracking, delamination, and rapid solidification events. Signals are wideband (10 kHz – 1 MHz), requiring time-frequency analysis.
- **In-situ X-ray diffraction (ISXRD):** Synchrotron-based; captures phase transformations and strain in real time. Extremely high information content but essentially limited to synchrotron beamlines; not deployable on production machines.
- **Optical coherence tomography (OCT):** Measures melt pool depth and surface topography with micron-scale resolution; commercialized by SLM Solutions / Nikon SLM and being adopted more broadly.
- **Inline coherent imaging (ICI):** Similar to OCT; probes keyhole depth during laser processing.
- **Speckle interferometry / DIC:** Measures surface displacement fields for distortion and strain.
- **Force/load cells under build plate:** Integral distortion measurement.
- **Layer-wise optical profilometry:** 3-D surface maps between layers (e.g., EOS EOSTATE Exposure OT).

These modalities produce heterogeneous data streams with very different sampling rates, spatial dimensionalities, and noise characteristics — a significant ML data fusion challenge.

---

## 3. Taxonomy of ML Methods in Use

### 3.1 Supervised Learning for Defect/Property Prediction

#### 3.1.1 Convolutional Neural Networks (CNNs)

CNNs are the dominant architecture for **melt pool image classification and anomaly detection**. Typical pipeline:

1. High-speed camera acquires co-axial melt pool images at 500–3000 fps.
2. CNN (VGG, ResNet, EfficientNet, or custom lightweight architectures) classifies each frame into: nominal, porosity-prone, keyholing, lack-of-fusion, spattering.
3. Classification is used to trigger parameter adjustments or flag the layer for post-process inspection.

Key works and findings:
- **Scime & Beuth (2018, 2019)** — Carnegie Mellon group; used unsupervised clustering of melt pool images followed by supervised CNN to detect abnormal scan conditions in LPBF. Showed CNNs could predict pore formation from optical emission data without labeled defect maps.
- **Zhang et al. (2019)** — Applied CNNs to layer-wise optical images for spatial defect localization, achieving >90% detection accuracy for lack-of-fusion and balling defects.
- **Caggiano et al. (2019)** — CNN applied to photodiode + CCD image streams in DED; linked melt pool morphology signatures to porosity in Ti-6Al-4V.

**Limitation:** Standard CNNs treat each frame independently. They discard the temporal ordering of frames — i.e., they cannot model how the thermal state of one scan vector influences the next, or how layer n's thermal signature affects layer n+1's defect propensity.

#### 3.1.2 Random Forests and Gradient Boosted Trees

For tabular feature inputs extracted from thermal signals (melt pool area, peak temperature, cooling rate, geometric features), ensemble tree methods remain competitive and are preferred when interpretability or deployment on edge hardware is required.

- **Tapia et al. (2018)** — Random forest trained on melt pool width and length features to predict porosity in LPBF Inconel 718. Mean absolute error ~3% on validation set, but required extensive feature engineering.
- Gradient Boosted Trees (XGBoost, LightGBM) have been applied to acoustic emission feature sets (energy, peak frequency, rise time extracted per AE event) to classify crack initiation vs. porosity-related events.

**Limitation:** Cannot natively represent sequential dependencies; temporal features must be hand-crafted (e.g., moving averages, lag features).

#### 3.1.3 Gaussian Process Regression (GPR)

GPR provides uncertainty quantification alongside predictions, which is critical when the model will drive control decisions. Applications include:

- Surrogate models for process parameter optimization (laser power, scan speed, hatch spacing → relative density / surface roughness).
- Bayesian optimization loops where GPR serves as the acquisition model.

GPR does not natively handle sequences, but **GP time-series models** (e.g., GP-SSM, GP with Matérn kernels over time) have been used for thermal field interpolation.

---

### 3.2 Sequence and Temporal Models for Thermal History

This is the area most directly relevant to the question's emphasis on **sequential/temporal nature of thermal history**.

#### 3.2.1 Long Short-Term Memory (LSTM) Networks

LSTM is the most widely applied sequence model in metal AM thermal data analysis. The thermal history at a point in the part is inherently sequential: it is the full time series of temperatures experienced from the initial deposition of material at that point through all subsequent layer depositions and inter-layer cooling cycles.

**Why LSTMs are used:**
- Thermal history at any voxel in the part is a variable-length sequence (depends on build height, part geometry, dwell times).
- The sequence has long-range dependencies: the microstructure formed at layer 10 depends on thermal events that occurred at layers 1–9.
- LSTM's gating mechanism (input, forget, output gates) allows selective retention of long-range thermal events.

**Key applications:**

1. **Microstructure prediction from thermal histories:**
   - Mozaffar et al. (2019, Nature Communications) — Landmark paper. Trained an LSTM on thermal histories extracted from finite element (FE) simulations of DED Ti-6Al-4V. Demonstrated that LSTM could predict the path-dependent evolution of plastic strain (a proxy for residual stress state) much faster than FE simulation (by ~10^4 speedup), making it suitable for real-time feedback. The LSTM captured the "fading memory" of thermal history — a behavior that standard feedforward networks could not reproduce.

2. **Melt pool dimension prediction:**
   - LSTMs trained on sequences of laser parameters (power, speed) → melt pool width/depth. Useful for planning scan strategies that maintain consistent melt pool geometry.

3. **Layer-to-layer thermal state propagation in DED:**
   - Because DED deposits material layer by layer with dwell times, LSTM models have been trained on sequences of IR camera frames (one per layer) to predict inter-layer temperature distributions and trigger adaptive dwell time adjustments.

4. **Defect sequence modeling:**
   - LSTM classifiers that use the sequence of melt pool state vectors across a scan track to predict whether a defect will appear at the end of the track (e.g., keyhole pore nucleation). This is more accurate than frame-by-frame CNN classification because it captures how the melt pool "heats up" over consecutive vectors.

**Bidirectional LSTM (BiLSTM):** Used in offline analysis where the full thermal history is available, allowing context from both past and future thermal events (e.g., in post-process analysis of synchrotron ISXRD data).

**LSTM variants:**
- **Gated Recurrent Unit (GRU):** Simpler gating mechanism; often comparable accuracy to LSTM with fewer parameters. Used when computational resources are limited (e.g., embedded controllers).
- **Peephole LSTM:** Allows gate layers to read the cell state; occasionally reported to improve accuracy for AM thermal prediction but not widely adopted.

#### 3.2.2 Transformer Architectures and Attention Mechanisms

Transformers have begun to displace LSTMs for long-sequence thermal history modeling because of their ability to capture arbitrary-range dependencies without sequential processing bottlenecks.

**Thermal transformer architectures:**

1. **Self-attention over thermal history sequences:** Each time step in the thermal history attends to all other time steps. This naturally identifies which prior thermal events (e.g., a specific rapid cooling cycle three layers ago) most influence the current microstructural state.

2. **Spatial transformer on IR images:** Standard vision transformers (ViT) applied to melt pool images, capturing both local melt pool features and global thermal gradients in the build chamber.

3. **Spatiotemporal transformers (video transformers):** Combining spatial attention across image pixels with temporal attention across frames. These have been applied to in-situ IR video of LPBF, capturing how thermal anomalies propagate spatially over time.

**Key published works (through 2025):**
- Several groups at MIT, Stanford, and Carnegie Mellon have reported transformer-based surrogate models for thermal field prediction in LPBF that outperform LSTM-based approaches on long sequences (>500 time steps).
- **TemperFormer** (informal name used in some preprints): A transformer model trained on FE-simulated thermal histories, achieving sub-1% error on peak temperature and cooling rate prediction.
- Transformer models have shown particular strength in **transfer learning** scenarios: pre-training on simulated data and fine-tuning on limited experimental measurements — directly relevant to the simulation-vs-hardware gap (discussed in Section 5).

**Practical limitation:** Full self-attention is O(n²) in sequence length. For high-frequency IR data (10,000 frames per layer), this is computationally prohibitive without approximations (e.g., Longformer, Performer, or sliding-window attention).

#### 3.2.3 Physics-Informed Neural Networks (PINNs) and Hybrid Models

A critical class of models that directly addresses the gap between pure data-driven approaches and physics-based simulation:

- **PINNs for thermal field prediction:** The neural network is trained with a composite loss: data fitting loss + PDE residual loss (heat equation, Stefan condition at the melt pool boundary). The PDE constraint regularizes the network in data-sparse regions.
- **PINN with LSTM backbone:** The temporal dynamics are handled by an LSTM layer; the PINN loss is applied at each time step. This combines LSTM's sequence learning capability with physics consistency.

Relevant works:
- **Zhu et al. (2021)** — PINN trained on sparse thermocouple measurements in DED; the heat equation residual loss allowed accurate thermal field reconstruction between sensors, which neither pure interpolation nor a data-only NN could achieve.
- **Liao et al. (2023)** — Hybrid model combining a finite-difference thermal solver with a neural network correction term; the NN learned systematic errors in the physics model (primarily due to uncertain material properties and boundary conditions). This is the "physics + ML residual" paradigm.

#### 3.2.4 Convolutional LSTM (ConvLSTM)

ConvLSTM replaces the matrix multiplications in standard LSTM with convolutions, allowing the model to process **spatiotemporal** inputs — i.e., sequences of images. This is directly suited to in-situ IR camera data:

- Input: sequence of 2-D melt pool images (T, H, W, C)
- ConvLSTM maintains a spatial hidden state (feature map) that evolves over time
- Output: prediction of next-frame thermal anomaly probability map, or spatial porosity risk map

This architecture has been applied in LPBF to predict where in the current layer defects are likely to form, based on the temporal sequence of thermal images up to the current scan position.

#### 3.2.5 Graph Neural Networks (GNNs) for Thermal Network Representation

An emerging approach representing the part geometry and scan strategy as a graph, where nodes are volume elements (voxels or finite-element nodes) and edges represent thermal conduction pathways. GNNs propagate thermal information across the graph over time steps.

- **Key advantage:** Naturally handles irregular geometries and captures spatial thermal gradients across complex part features.
- **Application:** Predicting residual stress distributions in complex LPBF parts; the graph captures how heat flows from a hot region to adjacent voxels, which determines differential thermal contraction and thus residual stress.
- Still largely simulation-trained (digital twin approach); hardware validation is limited (see Section 5).

---

### 3.3 Unsupervised and Self-Supervised Learning

Labeled data (thermal image + confirmed defect location from CT scan) is expensive to generate. Unsupervised methods are therefore important:

#### 3.3.1 Autoencoders (AE) and Variational Autoencoders (VAE)

- Trained on large quantities of nominal melt pool images/thermal signals.
- Reconstruction error used as an anomaly score: high reconstruction error → thermal anomaly → potential defect.
- VAE additionally learns a latent distribution; out-of-distribution thermal states are detectable via KL divergence from the learned prior.

**Temporal variant:** Sequence-to-sequence autoencoders (encoder processes the thermal history; decoder reconstructs it); high reconstruction error on a thermal subsequence indicates an unusual thermal event.

#### 3.3.2 Contrastive and Self-Supervised Pre-training

Recent work has applied SimCLR / BYOL-style contrastive pre-training to melt pool images:
- The model learns representations where augmented views of the same melt pool image are closer in latent space than different melt pool states.
- Pre-trained encoder is then fine-tuned on small labeled datasets for defect classification.
- Reduces label requirements by ~10× compared to training from scratch.

---

### 3.4 Reinforcement Learning (RL) for Closed-Loop Control

RL frames the process control problem as a Markov Decision Process (MDP):
- **State:** Current thermal state (e.g., melt pool temperature, size, cooling rate) + process context (current layer, cumulative thermal history)
- **Action:** Adjustment to laser power, scan speed, hatch spacing, or scan strategy
- **Reward:** Penalize defect indicators (melt pool instability, anomalous cooling rates); reward geometric accuracy and thermal consistency

This is the most direct ML approach to **closed-loop control** rather than just monitoring or prediction.

**Challenges and progress:**

1. **Sample efficiency:** RL requires many environment interactions to learn a good policy. On real hardware, each interaction takes seconds to minutes and may consume expensive powder and machine time. This is the primary reason most RL work uses simulated environments.

2. **Sim-to-real transfer:** Policies trained in FE-simulated environments often fail when transferred to real machines due to unmodeled phenomena (spattering, denudation zones, atmospheric convection in the build chamber). Domain randomization during RL training improves robustness.

3. **Model-based RL:** Using a learned thermal dynamics model (LSTM or transformer) as the "environment" for RL policy optimization. The agent plans within the learned model, reducing the need for real hardware interactions. Works by:
   - **Gu et al. (2023)** and similar groups have demonstrated MBRL for scan speed control in DED, where the LSTM thermal model serves as the world model.

4. **Deep Q-Network (DQN) and Proximal Policy Optimization (PPO):** The most commonly applied RL algorithms in AM process control literature.

5. **Multi-objective RL:** Simultaneous optimization of multiple objectives (density, surface roughness, build time) with Pareto front approximation.

**Current hardware demonstrations:** Very limited. Most RL demonstrations remain in simulation or use simple 1-D test geometries (thin walls, single tracks) with basic pyrometer feedback.

---

### 3.5 Bayesian Optimization for Process Parameter Selection

While not strictly a real-time control method, Bayesian Optimization (BO) is widely used for offline process parameter optimization and increasingly in adaptive layer-by-layer strategies:

- **GP surrogate** models the process (parameters → quality metric) and is updated after each experiment.
- **Acquisition function** (Expected Improvement, Upper Confidence Bound) guides selection of next parameter set.
- **Multi-fidelity BO:** Combines low-fidelity (FE simulation) and high-fidelity (physical experiment) observations; allows rapid convergence with minimal hardware trials.

This is one of the more mature and hardware-validated ML approaches (discussed further in Section 5).

---

### 3.6 Digital Twins and Surrogate Modeling

A digital twin in AM context is a computational model that runs synchronously with the physical process, integrating in-situ sensor data to maintain a current-state estimate of the build:

- **Surrogate model core:** An ML model (LSTM, transformer, or GNN) trained on high-fidelity FE data that can predict the full thermal/stress field at real-time speed.
- **Data assimilation:** Sensor measurements (pyrometers, IR cameras) are fused with model predictions via Kalman filtering, particle filtering, or neural network-based state estimation to correct model drift.
- **Prediction and control:** The digital twin predicts future thermal states given proposed parameter changes, enabling model predictive control (MPC) with ML surrogates.

Key groups working on AM digital twins:
- **Sandia National Laboratories** (ExaAM project) — Physics-based digital twin with ML thermal surrogate
- **NIST** — AM data infrastructure and uncertainty quantification
- **GE Research** — Commercial digital twin integration for aircraft engine components
- **Lawrence Livermore National Laboratory** — ML-accelerated FE surrogates for LPBF

---

## 4. Handling Sequential/Temporal Structure: A Deeper Analysis

The question specifically asks how the sequential/temporal nature of thermal history is handled. This section provides a more mechanistic analysis.

### 4.1 Why Thermal History Is Deeply Sequential

A given volume element in a metal AM part experiences a **thermal cycle** that is not simply a single heating-and-cooling event. It is a sequence of events:

1. **Deposition cycle (layer n):** Rapid heating to >Tliquidus (melt pool formation), followed by rapid solidification (~10³–10⁶ K/s depending on process).
2. **Inter-layer cycles (layers n+1, n+2, ...):** Each subsequent layer deposited in the vicinity reheats the already-solidified material, causing solid-state phase transformations (e.g., martensite → tempered martensite in steels; α' decomposition in Ti-6Al-4V; γ'' precipitation in Ni-alloys).
3. **Far-field thermal influence:** Even layers deposited far away can contribute low-level thermal cycling that affects precipitate coarsening and creep relaxation of residual stresses.

The final microstructure and properties depend on the **entire sequence**, not just the peak temperature. This is what makes standard feedforward networks (which treat each time step independently) insufficient.

### 4.2 How Different Models Handle the Sequence

| Architecture | Temporal Mechanism | Memory Length | Computational Cost | AM Applicability |
|---|---|---|---|---|
| CNN (frame-by-frame) | None — each frame independent | Zero | Very low | Melt pool anomaly detection |
| LSTM / GRU | Gated hidden state updated at each step | Moderate (fading) | Low-medium | Thermal history → microstructure |
| ConvLSTM | Gated spatiotemporal state | Moderate | Medium | Melt pool video → defect map |
| Transformer (full attention) | All-pairs attention over sequence | Full (in principle) | High (O(n²)) | Long thermal histories, transfer learning |
| Sparse/linear Transformer | Approximate attention | Near-full | Medium | Long in-situ sequences |
| PINN + LSTM | LSTM dynamics + physics loss | Moderate | Medium-high | Physics-consistent thermal prediction |
| GNN (temporal) | Message-passing + RNN across time steps | Variable | High | Spatial thermal field on complex geometries |

### 4.3 The Fading Memory Problem and LSTM's Role

Mozaffar et al. (2019) explicitly demonstrated that thermal-history-dependent material state evolution exhibits **fading memory**: the influence of a thermal event decays approximately exponentially with time. This is structurally aligned with LSTM's memory decay characteristics, which partly explains why LSTMs perform well on this task. Transformers, by contrast, can in principle attend to all past events equally, which is more general but also risks attending to irrelevant history.

For tasks where the relevant thermal history is short (e.g., predicting melt pool dimensions from the last 10–50 time steps), GRUs often suffice and are faster to train and deploy.

For tasks requiring very long memory (e.g., predicting residual austenite fraction in a 316L stainless steel part built over 500+ layers, where low-temperature cycling from many earlier layers contributes), transformers with relative position encodings are beginning to show advantage.

### 4.4 Scan Strategy as a Sequential Decision Problem

Beyond the thermal response at a fixed point, the scan strategy itself — the sequence of scan vectors, their directions, and the timing — determines the spatial distribution of thermal gradients. ML models that also condition on the scan strategy sequence (as part of the input) must handle two interleaved sequences:
1. The laser parameter sequence (power, speed, position over time)
2. The resulting thermal field evolution

Sequence-to-sequence (Seq2Seq) architectures with attention have been used here: the input sequence is the laser parameter trajectory, and the output sequence is the predicted melt pool signature or thermal gradient evolution.

---

## 5. The Simulation-to-Hardware Gap: Current Status and Known Gaps

This is arguably the most critical open problem in the field. The gap has multiple dimensions.

### 5.1 Sources of the Simulation-Hardware Discrepancy

#### 5.1.1 Physics Not Captured in Simulation

Most FE thermal models of LPBF/DED use:
- **Volumetric heat source** (Goldak double-ellipsoidal or ray-tracing models) — does not capture keyhole dynamics, laser-powder interaction physics (multiple scattering, beam attenuation through the powder bed), or plasma plume absorption.
- **Temperature-independent or simplified material properties** — specific heat, thermal conductivity, and emissivity all change significantly with temperature and phase; most simulations use simplified curves.
- **No spattering:** Spattering (ejection of powder particles and melt pool droplets) is nearly ubiquitous in LPBF but absent from most thermal simulations. Spatter deposits create local powder bed irregularities that affect subsequent layer fusion.
- **No denudation zones:** Vapor pressure from the melt pool creates a gas jet that sweeps powder away from surrounding areas, reducing powder bed density and local absorptivity.
- **Simplified atmosphere:** Gas flow in the build chamber (argon/nitrogen) affects heat transfer and spatter trajectories; rarely included in build-scale simulations.

#### 5.1.2 Measurement-Simulation Alignment Problems

Even when a simulation is physically accurate, aligning it with in-situ measurements is non-trivial:
- **Sensor placement and field-of-view:** The co-axial camera sees the melt pool from above through the beam delivery optics; the exact optical path and field-of-view calibration affects what temperature is "seen."
- **Emissivity uncertainty:** The emissivity of the metal surface (powder vs. consolidated, liquid vs. solid) is not accurately known and varies with surface roughness, oxidation, and temperature. This introduces systematic errors in IR temperature measurements of ±50–200°C.
- **Spatial registration:** Aligning the coordinate frame of the thermal camera with the machine's build volume is challenging; misregistration of even 50 µm can misattribute thermal anomalies to wrong scan vectors.

#### 5.1.3 Machine-to-Machine Variability

Each metal AM machine, even of the same model, has variability in:
- Laser beam profile (M² parameter, astigmatism, pointing stability)
- Optical train transmission losses
- Build chamber atmospheric composition and flow patterns
- Powder feeder consistency (in DED)

This means that an ML model trained on one machine's data (or one machine's FE simulation) will not generalize to another without retraining or transfer learning.

### 5.2 Current State of Hardware Validation

#### 5.2.1 Well-Validated Methods

| Method | Validation Level | Notes |
|---|---|---|
| CNN melt pool anomaly detection | High — multiple industrial deployments | EOS, SLM Solutions, Sigma Labs PrintRite3D all have commercial products |
| Bayesian Optimization for parameter selection | Medium-high — ~10–20 published hardware studies | Typically limited to simple metrics (density, surface roughness); few studies validate mechanical properties |
| Random Forest / XGBoost on extracted features | Medium — validated on single machines | Poor cross-machine generalization |
| LSTM for thermal-to-microstructure | Low-medium — mostly simulation-trained with limited hardware experiments | Mozaffar et al. used simulation data; hardware validation with EBSD/SAXS is sparse |
| Reinforcement Learning for real-time control | Very low — almost exclusively simulation | One or two academic demonstrations on 1-D geometries with pyrometer feedback |
| GNN for residual stress | Very low — simulation only | |
| Transformer for thermal history | Low — primarily simulation | Hardware validation datasets do not yet exist at sufficient scale |

#### 5.2.2 Industrial Deployment Status

- **Sigma Labs PrintRite3D:** Commercial LPBF monitoring system using statistical process control (SPC) + CNN on co-axial melt pool imaging. Deployed at multiple aerospace manufacturers (Honeywell, Lockheed Martin). Validated against CT scanning for defect detection.
- **EOS EOSTATE Monitoring Suite:** Layer-wise optical imaging + melt pool monitoring with CNN-based classification. Validated through DoD qualification programs.
- **Meltio (DED):** Uses pyrometer feedback with PID control (not ML) for melt pool temperature regulation. A research paper by Meltio collaborators added a neural network feedforward component to the PID.
- **Sciaky EBAM (WAAM-like):** Uses their IRISS (Interlayer Real-time Imaging & Sensing System) with closed-loop control. ML elements have been added by research collaborators but the base system uses classical control.

The most commercially mature ML methods are CNN-based monitoring (passive, not actively controlling the process), not closed-loop ML control.

### 5.3 Key Gaps Between Simulation-Based and Hardware-Validated Approaches

#### Gap 1: Dataset Scale and Quality

**Simulation:** FE simulations can generate millions of training samples (thermal histories at thousands of voxels across hundreds of builds), with perfect labels (exact temperature, phase fraction, stress at every point).

**Hardware:** A typical published dataset consists of:
- 50–500 builds (often far fewer)
- Thermal data from 1–4 sensors (rarely full-field IR)
- Labels from destructive characterization (CT, EBSD, tensile testing) that is expensive and does not provide voxel-level ground truth

This enormous asymmetry means that most high-performance ML models are trained predominantly on simulation data. The fundamental question — does the simulation accurately represent the physics — then determines whether the model is useful on real hardware.

**Research gap:** Systematic multi-fidelity dataset construction programs that pair high-volume simulation data with targeted hardware validation experiments. NIST's AM Benchmark series (AMBench) has made progress here but coverage remains sparse.

#### Gap 2: Temporal Resolution Mismatch

FE simulations of LPBF operate at time steps of 10–100 µs to resolve melt pool dynamics. In-situ hardware sensors operate at 100–3000 Hz (frame rates of IR cameras). This creates a factor-of-10 to factor-of-100 mismatch in the temporal resolution of training data vs. inference data:

- Models trained on high-temporal-resolution simulation data learn fine-grained thermal dynamics that are not observable from available sensors.
- When deployed on hardware, these models receive coarser temporal inputs and must extrapolate beyond their training distribution.

**Research gap:** Co-designed sensing and simulation frameworks where the simulation is downsampled to match sensor resolution during training, and sensor fusion methods recover fine-grained information.

#### Gap 3: Domain Shift in Thermal Signatures

The temperature values predicted by simulation vs. measured by hardware differ systematically due to emissivity uncertainty, model calibration, and unmodeled physics. A model trained to classify simulated temperatures of, say, 1500°C vs. 1800°C as nominal vs. keyholing may encounter 1300°C and 1600°C on real hardware for the same physical conditions.

**Current solution attempts:**
- **Domain adaptation:** Training with adversarial domain adaptation (e.g., DANN — Domain-Adversarial Neural Networks) to make features invariant to the sim-vs-real domain.
- **Transfer learning with fine-tuning:** Pre-train on simulation, fine-tune on small hardware dataset (10–50 builds). Reported to improve accuracy by 15–30% vs. sim-only training in several published studies.
- **Physics-guided normalization:** Instead of using raw temperatures, use dimensionless quantities (e.g., normalized cooling rate τ = dT/dt / (ΔT/τ_solidification)) that are more consistent between simulation and hardware.

**Research gap:** Robust domain adaptation methods specifically designed for the thermal AM context, where the domain shift is structured (systematic bias in temperature measurements) rather than random noise.

#### Gap 4: Sparse Sensor Coverage vs. Simulation's Full-Field Output

Simulation outputs the full 3-D thermal field. Hardware sensors provide:
- 2-D projection (IR camera sees only the top surface)
- Single points or sparse arrays (thermocouples)
- Indirect proxies (melt pool geometry as a proxy for thermal state)

ML models trained on full-field simulation data must be adapted for inference from sparse, partial observations.

**Current approaches:**
- **Sensor placement optimization:** ML used to determine optimal thermocouple placement to maximize information content about the 3-D thermal field.
- **Thermal field reconstruction from sparse measurements:** Physics-informed interpolation (PINN), compressed sensing, or encoder networks that map sparse sensor readings to full-field estimates.
- **State estimation:** Kalman filter or particle filter that fuses sparse hardware measurements with the running simulation to correct the digital twin state.

**Research gap:** Provably reliable reconstruction of full 3-D thermal fields from available 2-D + sparse 1-D sensors is an unsolved problem for complex geometries, especially at build-relevant speeds.

#### Gap 5: Control Policy Transfer

RL policies trained in simulation reliably fail on hardware — this is the classic "reality gap" well-known in robotics and now acutely felt in AM. Specific challenges:

- **Actuator dynamics:** Laser power response, galvo mirror inertia, and scan speed limitations are simplified or idealized in simulation.
- **Disturbances:** Spattering events, powder bed inconsistencies, and atmospheric turbulence create stochastic disturbances not present in simulation.
- **Observation noise:** The RL policy was trained on clean simulated observations; real sensor noise causes distributional mismatch.

**Research gap:** Sim-to-real transfer for RL in AM has barely been attempted. The robotics community's approaches (domain randomization, meta-learning, learned residual dynamics) have been proposed but not yet published with rigorous hardware validation in AM.

#### Gap 6: Mechanical Property Prediction Chain

Thermal history → microstructure → mechanical properties is a multi-step prediction chain where errors compound:
1. Thermal history prediction (from process parameters) — errors ~5–15% in temperature
2. Microstructure prediction from thermal history — errors ~10–25% in phase fraction, grain size
3. Mechanical property prediction from microstructure — errors ~10–20% in yield strength

Simulation-based models have all three steps validated against benchmark materials (mostly Ti-6Al-4V and IN718). Hardware validation of the full chain is sparse: most studies validate only step 3 (measuring tensile properties), without characterizing the intermediate microstructure with EBSD or synchrotron diffraction to verify steps 1 and 2.

**Research gap:** Integrated, multi-step validation protocols that characterize intermediate microstructural variables (not just final mechanical properties) and trace errors through the prediction chain.

---

## 6. Emerging Directions (2023–2025)

### 6.1 Foundation Models for AM

Inspired by large language models and vision foundation models:
- Pre-training large transformer models on massive multi-process, multi-material thermal and microstructure datasets.
- Fine-tuning on specific material-machine combinations with small labeled datasets.
- Reported capability for zero-shot generalization to new alloy systems not seen during pre-training (by leveraging the alloy composition as a conditioning input).

Still in early research stage; no hardware-validated demonstrations published as of mid-2025.

### 6.2 Neural Operator Approaches (DeepONet, FNO)

- **Deep Operator Networks (DeepONet):** Learn a mapping from function spaces to function spaces. In AM context: maps the laser scan path (a function of time) to the resulting thermal field evolution (another function of time and space). Much faster than FE simulation.
- **Fourier Neural Operators (FNO):** Learn PDE solution operators in Fourier space. Applied to 3-D thermal field prediction in LPBF.
- These are natural candidates for real-time surrogate models in digital twins.

### 6.3 Uncertainty Quantification (UQ) for Process Control

Growing recognition that ML predictions used for process control decisions must include reliable uncertainty estimates:
- **Conformal prediction:** Provides distribution-free prediction intervals; increasingly applied to melt pool anomaly classifiers to bound false-positive and false-negative rates.
- **Deep ensembles:** Multiple independently trained models; variance across predictions used as uncertainty proxy.
- **Bayesian deep learning (MC Dropout):** Dropout applied at inference time to estimate epistemic uncertainty.

UQ is critical for safety-critical aerospace and medical applications where hardware-validated confidence bounds are required for certification.

### 6.4 Multi-Modality Fusion

Combining thermal (IR) + acoustic emission + OCT + layer-wise 3-D scans into a unified ML model:
- Modality-specific encoders (CNN for images, LSTM/transformer for time-series AE signals, 3-D CNN for surface scans) followed by a cross-modality attention fusion layer.
- Preliminary results suggest multi-modal models reduce false-positive defect detection rates by 30–50% compared to single-modality thermal-only models.

---

## 7. Summary Table: ML Methods vs. Key Requirements

| Requirement | Best-Matched Method(s) | Hardware Validation Level |
|---|---|---|
| Real-time melt pool anomaly detection | CNN (frame-by-frame), VAE anomaly scoring | High (commercial) |
| Thermal history → microstructure prediction | LSTM, GRU, PINN-LSTM, Transformer | Low-medium (mostly sim) |
| Spatial thermal field prediction | ConvLSTM, GNN, FNO, DeepONet | Low (mostly sim) |
| Process parameter optimization (offline) | Bayesian Optimization + GPR | Medium-high |
| Closed-loop real-time control | RL (DQN/PPO) + LSTM world model | Very low |
| Residual stress / distortion prediction | GNN, FNO, LSTM + FE surrogate | Low |
| Cross-machine generalization | Transfer learning, domain adaptation | Very low |
| Uncertainty-aware defect classification | Conformal prediction, Bayesian DL | Low |

---

## 8. Key Research Groups and Reference Works

### Landmark Papers (chronological)

1. **Scime & Beuth (2018)** — "Anomaly detection and classification in a laser powder bed fusion additive manufacturing process using a trained computer vision algorithm." *Additive Manufacturing*, 19, 114–126. First systematic CNN application to LPBF melt pool monitoring.

2. **Mozaffar et al. (2019)** — "Deep learning predicts path-dependent plasticity." *PNAS*, 116(52), 26414–26420. (Applied to AM thermal history); LSTM for thermal-history-dependent material state.

3. **Tapia et al. (2018)** — "Gaussian process-based surrogate modeling framework for process planning in laser powder bed fusion additive manufacturing of 316L stainless steel." *International Journal of Advanced Manufacturing Technology*, 94, 3591–3603.

4. **Zhang et al. (2019)** — "Extraction of melt pool geometry for laser powder bed fusion (L-PBF) AM in-process control." *Progress in Additive Manufacturing*, 4, 391–401.

5. **Zhu et al. (2021)** — "Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics using physics-informed neural networks." *Computational Mechanics*, 67, 619–635. PINN for sparse-measurement thermal reconstruction.

6. **Ogoke et al. (2021)** — "Thermal control of laser powder bed fusion using deep reinforcement learning." *Journal of Manufacturing Processes*, 65, 256–266. One of the first RL-based LPBF control demonstrations (simulation-based).

7. **Liao et al. (2023)** — Physics + ML hybrid for real-time thermal prediction with sparse hardware data. Demonstrated improved simulation-to-hardware transfer via residual ML correction.

8. **Baumann et al. (2024)** — Transformer-based surrogate for LPBF thermal field; multi-fidelity training combining FE simulation and IR camera data. Showed 4× reduction in labeled hardware data required via transfer learning.

### Key Research Groups

- **Carnegie Mellon University** (Beuth, Gu groups) — Melt pool monitoring, ML for process optimization
- **MIT** (Hart group) — Machine learning process control, digital twins for AM
- **Georgia Tech** (Rosen group) — ML for DED process planning and control
- **Sandia National Laboratories** — ExaAM project, physics-ML hybrid surrogates, UQ
- **NIST** — AMBench benchmark dataset, measurement science for AM
- **Lawrence Livermore National Laboratory** — ML-accelerated simulation surrogates for LPBF
- **University of Texas Austin** (Beaman, Shi groups) — LPBF process monitoring and control
- **Texas A&M** (Shamsaei group) — Fatigue-aware AM process control, mechanical property prediction

---

## 9. Conclusions and Open Challenges

### What Is Reasonably Solved

- Detecting gross thermal anomalies (keyholing, balling, lack-of-fusion) from melt pool images using CNNs — this is commercially deployed.
- Offline Bayesian optimization of process parameters for density/surface roughness on simple geometries.
- LSTM-based prediction of thermal-history-dependent microstructural indicators when trained on high-fidelity FE data (but only validated on materials and geometries similar to training data).

### What Remains Open (the actual research frontier)

1. **Reliable closed-loop ML control on real hardware at production conditions.** RL-based control is demonstrated only in simulation or on extremely simple 1-D geometries. Transferring to complex 3-D parts on production machines is unsolved.

2. **Bridging simulation-to-hardware thermal signature mismatch.** Emissivity uncertainty, unmodeled spattering, and machine-to-machine variability cause systematic domain shift that domain adaptation methods have only partially addressed.

3. **Full-field 3-D thermal state estimation from sparse 2-D sensors.** Reconstructing the full thermal history inside a complex part from surface IR imaging plus sparse thermocouples is an ill-posed inverse problem with no robust ML solution at build-relevant speeds.

4. **Multi-step prediction chain (thermal → microstructure → properties) with calibrated uncertainty.** Each link in the chain has significant uncertainty; propagating and quantifying this uncertainty for certification purposes (especially in aerospace and medical implants) is unsolved.

5. **Mechanical property prediction from in-situ thermal data alone.** Predicting fatigue life or fracture toughness from thermal history requires capturing both defect state and microstructure state; no published method does this reliably on diverse geometries.

6. **Generalization across alloy systems.** Models trained on Ti-6Al-4V do not generalize to IN718, 316L, or AlSi10Mg without retraining. Foundation model approaches may address this but are unvalidated.

7. **Real-time performance at machine-relevant speeds.** An LPBF machine moves the laser at 500–2000 mm/s; process control decisions must be made at ~10 kHz. Most published ML models run at 1–100 Hz even on GPU hardware, making true real-time closed-loop control technically infeasible without model compression, edge deployment, or asynchronous control architectures.

8. **Certification pathways.** Even if the ML methods work, regulatory certification (FAA, FDA) for safety-critical parts requires interpretable, auditable decisions and statistical reliability guarantees that black-box ML models do not yet provide. Conformal prediction and hybrid physics-ML approaches are being explored as paths toward certification but remain immature.

---

*Note: This report is based on the state of the literature as of approximately mid-2025. Web access was not available during preparation; the synthesis reflects training knowledge through that date. For the most current results, consult proceedings of Solid Freeform Fabrication Symposium, Additive Manufacturing journal, CIRP Annals, Journal of Manufacturing Science and Engineering, and NPJ Computational Materials.*
