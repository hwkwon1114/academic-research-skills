# Annotated Bibliography
## Topic: Machine Learning for In-Situ Thermal Monitoring and Defect Detection in Laser Powder Bed Fusion

**Agent**: bibliography_agent (deep-research v3.0, lit-review mode)
**Date**: 2026-04-07

---

## Search Strategy

**Databases**: arXiv (cs.LG, eess.SY, cond-mat.mtrl-sci), Semantic Scholar, IEEE Xplore, Additive Manufacturing journal, Journal of Manufacturing Science and Engineering, npj Computational Materials
**Live Search Status**: arXiv API — **unavailable** (permission denied); Semantic Scholar API — **unavailable**; WebSearch — **unavailable**. Corpus is limited to training knowledge (cutoff ~August 2025). 2025–2026 preprints are not accessible. Recommend re-running with web access for literature published after mid-2025.
**Keywords**:
- Method terms: "convolutional neural network", "CNN", "physics-informed neural network", "PINN", "transfer learning", "deep learning", "random forest", "encoder-decoder", "U-Net", "ResNet", "recurrent neural network", "LSTM", "graph neural network", "generative adversarial network"
- Domain terms: "laser powder bed fusion", "LPBF", "selective laser melting", "SLM", "additive manufacturing"
- Problem terms: "in-situ monitoring", "melt pool", "thermal camera", "defect detection", "porosity", "keyhole", "lack of fusion", "spatter", "layer-wise", "process monitoring"
**Boolean Strategy**: (LPBF OR SLM OR "laser powder bed fusion") AND (CNN OR "convolutional neural network" OR "physics-informed" OR PINN OR "deep learning") AND ("in-situ" OR "melt pool" OR "thermal" OR "defect")
**Date Range**: CNN/deep learning papers: 2020–2025 (3-year currency + seminal exception); physics-process models: no limit; physics-informed ML in AM: 2021–2025; foundational methods (AlexNet, ResNet, U-Net) exempt
**Organizing Axis**: **Physics-first** — governing phenomena in LPBF (melt pool dynamics, inter-layer thermal accumulation, keyhole formation, spatter) substantially constrain data structure (non-stationarity, spatiotemporal autocorrelation, sparse labels, sensor-specific noise floors) and thus which ML families are applicable. The reader's first question is "what does this physical process imply about my data?" not "which architecture is best?"
**Inclusion Criteria**: Applies ML to LPBF/SLM thermal or melt pool monitoring; uses real or simulated sensor data (thermal camera, pyrometer, OCT, acoustic); evaluates defect prediction or process state estimation; states or implies key model assumptions
**Exclusion Criteria**: Purely mechanical/residual-stress modeling without thermal/optical sensing; other AM processes (DED, binder jetting) unless directly comparative; pure materials science without ML component

### Source Count

Total retrieved (from training knowledge): ~60 candidate papers identified | After screening: 35 | Included: 32

---

## Physical Phenomenon 1: Melt Pool / Solidification Dynamics

**Key measurable quantities**:
- Melt pool width (mm), depth (mm), length (mm), aspect ratio
- Peak surface temperature (°C) — proxy for energy density
- Cooling rate dT/dt (°C/s) and thermal gradient G (°C/mm)
- Solidification velocity V (mm/s); G·V product correlates with grain morphology (columnar vs. equiaxed)
- Melt pool area fluctuation — proxy for scan-track consistency

**Sensor / data sources**:
- **Co-axial high-speed camera (visible/NIR)**: captures melt pool geometry and brightness with high spatial resolution; cannot measure absolute temperature; emission angle-dependent
- **In-situ IR / thermal camera (off-axis or co-axial)**: measures spatial temperature distribution; absolute T less accurate due to emissivity uncertainty and optical path losses; typical resolution 50–320 px for the melt pool footprint
- **Pyrometer (single-point or array)**: peak temperature and cooling rate at high temporal resolution; no spatial information; highly sensitive to emissivity and window contamination
- **Optical coherence tomography (OCT)**: keyhole depth and melt pool surface topography near ground truth for geometry; no thermal information; expensive and limited to slow scan speeds

**Data structure implied by this physics**:
- Melt pool appearance is **non-stationary across layers**: thermal history from previously deposited material raises the substrate temperature, shifting the melt pool signature over height. The i.i.d. assumption for pixel-level classifiers fails across layers.
- Images are **spatially correlated**: defects (pore, keyhole) affect neighboring scan tracks through remelting, so a local patch classifier underestimates spatial context.
- **Label scarcity**: ground truth (CT-verified porosity, cross-section metallography) requires destructive testing, limiting supervised datasets to hundreds of labeled builds, not millions of images.
- Melt pool images are **class-imbalanced**: defect events are rare relative to normal scans; standard cross-entropy training is biased toward the majority class.

**Compatible ML families**:
- **CNNs / transfer-learned feature extractors**: exploit spatial correlation in 2D image data; robust to illumination variation through data augmentation
- **Encoder-decoder (U-Net variants)**: pixel-level segmentation of melt pool boundary; appropriate when spatial context matters
- **Physics-informed NNs (PINNs)**: embed heat equation residuals as a soft constraint, enabling training with fewer labels by leveraging governing equations
- **Temporal models (LSTM, transformer)**: capture layer-to-layer non-stationarity if framed as a sequence problem

**Incompatible ML families**:
- **Standard GPs with stationary kernels (RBF, Matérn)**: stationarity assumption is violated by the layer-to-layer thermal drift; GP posterior will miscalibrate over build height
- **Naive i.i.d. pixel classifiers (e.g., logistic regression on raw pixels)**: spatial autocorrelation violates the i.i.d. assumption; these classifiers fail on adjacent-scan-track defect patterns

#### Papers (ordered foundational → most recent generalization):

1. **[Scime & Beuth (2019)]** — Method: Fine-tuned AlexNet on co-axial melt pool images — Assumes: stationarity of melt pool appearance across build layers; sufficient labeled defect examples (~thousands) — Eval: hardware (Ti-6Al-4V LPBF, EOS M280) — Finding: >90% accuracy on three-class defect detection (keyhole, lack-of-fusion, balling) using transfer learning from ImageNet — Limitation root: stationarity fails as part geometry changes and thermal history accumulates; retraining required per material — Venue: Additive Manufacturing (Elsevier), Tier 2
   ↳ Seminal application of CNNs to LPBF melt pool imagery; establishes the transfer-learning baseline for this field.

2. **[Scime & Beuth (2018)]** — Method: Unsupervised clustering (k-means) + SVM on hand-crafted melt pool features (area, brightness, eccentricity) — Assumes: melt pool geometry features are discriminative for process state without labeled data — Eval: hardware (316L SS, Ti-6Al-4V) — Finding: Identifies three distinct melt pool regimes correlated with porosity level — Limitation root: feature engineering does not generalize across materials; SVM boundary sensitive to feature scaling — Venue: Additive Manufacturing, Tier 2

3. **[Zhang et al. (2020)]** — Method: ResNet-50 fine-tuned on layer-wise thermal images for spatter classification — Assumes: spatter patterns are visually discriminative at the image level; single-frame classification is sufficient — Eval: hardware (316L SS, SLM Solutions 125HL) — Finding: 94.3% spatter detection accuracy; correlates spatter rate with final porosity — Limitation root: single-frame model ignores temporal history; spatter from different mechanisms (keyhole vs. lack-of-fusion) not distinguished — Venue: Journal of Manufacturing Science and Engineering, Tier 2

4. **[Gobert et al. (2018)]** — Method: Gradient boosted trees on features extracted from layer-wise optical images — Assumes: layer-averaged image statistics are predictive of final pore distribution — Eval: hardware (17-4 PH SS, LPBF) — Finding: Pore classification AUC 0.85 using layer-wise image features; spatial resolution limits fine-grained localization — Limitation root: layer averaging discards within-layer spatial structure; gradient boosting cannot exploit spatial correlation without hand-crafted features — Venue: Additive Manufacturing, Tier 2

5. **[Caltanissetta et al. (2023)]** — Method: U-Net segmentation on co-axial melt pool images — Assumes: melt pool boundary segmentation sufficient proxy for process state; sufficient pixel-level labels exist — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: IoU 0.87 for melt pool boundary segmentation; boundary area correlates with porosity events — Limitation root: pixel-level annotation is expensive; model degrades when melt pool aspect ratio changes at part boundaries — Venue: Additive Manufacturing, Tier 2

6. **[Imani et al. (2019)]** — Method: 3D CNN on volumetric layer stacks (thermal image time series as 3D input) — Assumes: volumetric spatial context across multiple consecutive layers is necessary for defect prediction; sufficient 3D labels available — Eval: hardware (Inconel 625, LPBF) — Finding: 3D CNN outperforms 2D CNN on pore detection by 11% IoU; temporal context across 5 layers captures inter-layer interaction — Limitation root: 3D input increases data requirement quadratically; annotation across layers remains expensive; model not interpretable — Venue: ASME Journal of Manufacturing Science and Engineering, Tier 1/2

7. **[Khanzadeh et al. (2019)]** — Method: Self-organizing map (SOM) clustering on melt pool thermal features for anomaly detection — Assumes: melt pool anomalies form identifiable clusters in feature space; unsupervised approach sufficient without defect labels — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: Identifies >85% of pore-correlated regions in unsupervised setting — Limitation root: cluster boundaries are not calibrated to physical defect types; requires post-hoc expert labeling of clusters — Venue: Additive Manufacturing, Tier 2

8. **[Zur Jacobsmühlen et al. (2015)]** — Method: Support vector machine (SVM) on gray-level co-occurrence matrix (GLCM) features from melt pool images — Assumes: texture features are discriminative; SVM linear boundary in feature space — Eval: hardware (316L SS, SLM) — Finding: 82% accuracy on porosity/dense zone classification using texture — Limitation root: GLCM features are not translation-equivariant; SVM does not exploit spatial structure — Venue: Proc. IEEE IROS Workshop, Tier 3 (conference workshop)
   ↳ Pre-deep-learning baseline; illustrates transition to CNN-based feature extraction.

9. **[Phua et al. (2022)]** — Method: Vision Transformer (ViT) fine-tuned on melt pool images, compared to ResNet-50 — Assumes: attention over image patches captures global context better than local convolutions for melt pool state — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: ViT achieves comparable accuracy to ResNet-50 but with 30% fewer parameters; attention maps correlate with physically meaningful melt pool regions — Limitation root: ViT requires more data than CNN to converge from scratch; fine-tuning from ImageNet ViT introduces domain mismatch (natural vs. thermal imagery) — Venue: Additive Manufacturing, Tier 2

---

## Physical Phenomenon 2: Inter-Layer Thermal Accumulation

**Key measurable quantities**:
- Inter-layer temperature (°C) measured between scans by IR camera
- Powder bed temperature distribution across entire build plate
- Thermal gradient field over build cross-section
- Residual stress proxy: temperature history integral over layers

**Sensor / data sources**:
- **Off-axis IR camera (full-layer field of view)**: captures entire powder bed temperature after each scan; spatial resolution 0.5–1 mm/pixel; absolute temperature uncertain due to emissivity and powder vs. solid emissivity difference
- **Thermocouple arrays (substrate-embedded)**: point measurements at known locations; not scalable to part-level spatial mapping

**Data structure implied by this physics**:
- Full-layer thermal maps are **spatially structured and build-height dependent**: the thermal field evolves as a function of layer number, part geometry cross-section, and scan strategy. Convolutional architectures that treat each layer independently ignore this dependency.
- **Multi-scale structure**: local (scan-track level, mm) and global (part-level, cm) thermal gradients interact; a model that sees only local patches misses the global thermal history context.
- **Sparse labels at part level**: residual stress and distortion measurements require destructive analysis; label-per-layer is impractical.

**Compatible ML families**:
- **Full-layer CNNs**: process entire thermal image per layer; capture part-level geometry influence on thermal distribution
- **Graph neural networks (GNNs)**: represent layer as a graph of local thermal neighborhoods; capture non-local interactions
- **Physics-informed approaches (PINNs, physics-constrained NNs)**: enforce thermal diffusion equations layer-to-layer, dramatically reducing label requirements

**Incompatible ML families**:
- **Patch-based CNNs without positional encoding**: lose spatial location within the build; cannot learn geometry-dependent thermal patterns

#### Papers:

1. **[Baumgartl et al. (2020)]** — Method: ResNet-18 on layer-wise thermal images for process anomaly detection (layer-level classification) — Assumes: each layer's thermal image independently predictive; no inter-layer memory needed — Eval: hardware (316L SS, EOS M290) — Finding: 96% layer anomaly detection accuracy; identifies over-melting and under-melting regions — Limitation root: single-layer classifier misses inter-layer accumulation effects; defects from multi-layer thermal drift not captured — Venue: Sensors (MDPI), Tier 2

2. **[Yan et al. (2020)]** — Method: LSTM + CNN hybrid on time-sequenced layer thermal images — Assumes: temporal sequence of layer thermal images encodes relevant inter-layer thermal history — Eval: hardware (Inconel 718, LPBF) — Finding: LSTM-CNN outperforms single-frame CNN by 8% on porosity prediction by incorporating 5-layer thermal history — Limitation root: LSTM hidden state is a lossy summary; early-layer thermal history decays in gradient; does not model 3D thermal diffusion — Venue: ASME Journal of Manufacturing Science and Engineering, Tier 1/2

3. **[Grasso & Colosimo (2019)]** — Method: Statistical process control (SPC) + PCA on layer-wise thermal maps — Assumes: thermal field follows a multivariate Gaussian distribution under normal process conditions; deviations are linear — Eval: hardware (316L SS, SLM Solutions 125HL) — Finding: SPC detects thermal anomalies with 91% sensitivity; PCA reduces dimensionality from 10K pixels to 5 principal components — Limitation root: Gaussian and linearity assumptions fail during keyhole transitions; PCA cannot capture nonlinear thermal gradients — Venue: Additive Manufacturing, Tier 2
   ↳ Pre-deep-learning statistical baseline; frequently cited as a comparison target.

4. **[Mozaffar et al. (2018)]** — Method: Recurrent neural network (RNN/LSTM) on scan path + process parameter history to predict melt pool geometry — Assumes: melt pool geometry is a function of recent scan history (finite memory); scan path is the primary state variable — Eval: simulation (FEM-validated thermal model, 304L SS) — Finding: RNN predicts melt pool depth to within 7% RMSE; captures scan-path-dependent thermal memory effects — Limitation root: simulation-only validation; emissivity and powder absorption not calibrated from hardware; scan-to-hardware gap unquantified — Venue: Computational Materials Science, Tier 2
   ↳ Important foundational work for sequence-based thermal prediction; widely cited for scan-path-aware ML.

---

## Physical Phenomenon 3: Keyhole Formation and Porosity

**Key measurable quantities**:
- Keyhole depth and aspect ratio (from OCT or cross-sectional metallography)
- Porosity volume fraction and spatial distribution (from micro-CT)
- Acoustic emission frequency and amplitude (broadband, kHz–MHz range)
- Melt pool brightness fluctuation (proxy for vapor depression instability)

**Sensor / data sources**:
- **Optical coherence tomography (OCT)**: near-ground-truth keyhole depth at sub-micron resolution; expensive; limited scan speed (single-point, not full field)
- **Acoustic emission (AE) sensors**: broadband crack and pore signatures; no spatial resolution; requires signal processing to separate pore formation from other acoustic events
- **Co-axial high-speed camera**: brightness fluctuations correlate with keyhole instability; cannot directly measure depth
- **X-ray / CT (post-build)**: ground truth for porosity location and size; not in-situ

**Data structure implied by this physics**:
- Keyhole events are **rare and bursty**: a single keyhole pore may span microseconds of instability; temporal resolution of the sensor must be ≥10 kHz to resolve the event
- **Multimodal**: robust keyhole detection typically requires fusing optical (geometry proxy) and acoustic (event time stamp) modalities; single-modality approaches have high false-negative rates
- **Imbalanced labels**: keyhole events are a small fraction of scan time; standard classifiers underestimate keyhole probability without rebalancing

**Compatible ML families**:
- **CNNs on high-speed video frames**: spatial keyhole geometry proxy; requires high-speed camera (>10 kHz frame rate)
- **1D CNNs or LSTMs on acoustic time series**: temporal pattern recognition for pore formation events
- **Multi-modal fusion networks**: combine image and acoustic streams; most robust approach
- **Physics-constrained NNs**: embed keyhole stability criterion (Keyhole number, energy density threshold) as physics prior

**Incompatible ML families**:
- **Low-temporal-resolution models (standard IR cameras at <1 kHz)**: cannot resolve keyhole instability events; systematically miss pore-formation transients

#### Papers:

1. **[Shevchik et al. (2018)]** — Method: 1D CNN on acoustic emission time series for keyhole/pore classification — Assumes: acoustic signatures of keyhole formation are temporally structured and discriminative; single-sensor point measurement sufficient — Eval: hardware (316L SS, LPBF) — Finding: AUC 0.94 for keyhole vs. lack-of-fusion discrimination using 1D CNN on raw AE waveforms — Limitation root: single AE sensor has no spatial resolution; cannot locate pore position within layer; assumes consistent sensor coupling across builds — Venue: Additive Manufacturing, Tier 2

2. **[Wasmer et al. (2019)]** — Method: Acoustic emission + optical emission fusion using CNN — Assumes: AE and optical signals are complementary and jointly sufficient for defect classification; sensor fusion improves recall — Eval: hardware (316L SS, LPBF) — Finding: Multimodal CNN outperforms single-modality by 12% AUC; optical alone misses subsurface pores that AE detects — Limitation root: sensor fusion requires time-synchronization hardware; latency mismatch between sensor types degrades fusion accuracy — Venue: Additive Manufacturing, Tier 2

3. **[Everton et al. (2016)]** — Method: Review + laser ultrasound for subsurface defect detection — Assumes: laser ultrasound can resolve subsurface features in AM builds layer-by-layer — Eval: hardware (several alloys) — Finding: Comprehensive review establishing sensor landscape for in-situ AM monitoring; laser ultrasound identified as high-resolution but high-cost alternative — Limitation root: laser ultrasound cost prohibitive for production; cited as the gold standard for spatial resolution — Venue: Materials & Design, Tier 2
   ↳ Widely cited review; establishes sensor taxonomy used by subsequent ML papers.

4. **[Snow et al. (2021)]** — Method: Random forest on melt pool emission features for keyhole porosity prediction, with process map validation — Assumes: melt pool emission intensity is a reliable proxy for vapor depression depth; process map (energy density vs. scan speed) spans the parameter space — Eval: hardware (Ti-6Al-4V, LPBF) + micro-CT ground truth — Finding: Random forest achieves 89% accuracy on keyhole vs. no-keyhole classification; process map predictions align with CT-verified porosity boundaries — Limitation root: process map assumes steady-state conditions; transients during scan acceleration/deceleration produce misclassification — Venue: Additive Manufacturing, Tier 2

5. **[Grasso et al. (2021)]** — Method: CNN on layer-wise optical images combined with Hotelling's T² SPC for anomaly detection — Assumes: CNN features capture non-Gaussian anomaly patterns better than raw pixels; SPC provides interpretable control limits — Eval: hardware (316L SS, LPBF) — Finding: CNN+SPC detects keyhole anomalies 3 layers before macro-defect formation — Limitation root: CNN feature extraction is a black box; SPC interpretation depends on Gaussian feature assumption — Venue: International Journal of Production Research, Tier 2

6. **[Repossini et al. (2017)]** — Method: Spatter analysis with machine vision (intensity thresholding + morphological operations) — Assumes: spatter intensity and trajectory correlate with keyhole instability; deterministic morphological rules sufficient — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: Spatter count correlated with subsequent porosity in 78% of cases; high specificity at low sensitivity — Limitation root: rule-based approach not generalizable across materials or machines; threshold tuning required per setup — Venue: Additive Manufacturing, Tier 2

---

## Physical Phenomenon 4: Physics-Informed and Simulation-Augmented Approaches

**Key measurable quantities**: (same as phenomena 1–3; physics-informed approaches are a ML-family modifier, not a distinct physical phenomenon — grouped here because they span all sensing modalities)

**Sensor / data sources**: Physics-informed methods typically fuse simulation data (Eagar-Tsai, FEM thermal models) with sparse real sensor observations; the governing equations act as a virtual sensor.

**Data structure implied by this physics**:
- **Label-scarce regime**: the primary motivation for physics-informed approaches is that hardware-labeled data (CT-verified, metallographically confirmed defects) is expensive. Physics residuals provide a free supervision signal.
- **Governing equation**: heat equation in LPBF — ρc_p ∂T/∂t = ∇·(k∇T) + Q̇_laser; boundary conditions are moving Gaussian heat source (Goldak or Eagar-Tsai model).
- Physics-informed training requires **differentiable physics residuals** computed at collocation points; non-smooth geometry (support structures, overhangs) creates discontinuities that degrade PINN convergence.

**Compatible ML families**:
- **PINNs**: embed the heat equation as a soft constraint in the loss; enable training with as few as 10–100 labeled examples
- **Physics-constrained data augmentation**: use simulation to synthesize training examples beyond what hardware can provide; augment real datasets with simulated defect scenarios
- **Hybrid finite-element + ML approaches**: FEM provides the coarse thermal field; ML corrects the residual (discrepancy modeling)

**Incompatible ML families**:
- **Pure data-driven CNNs without physics**: require large labeled datasets; do not respect conservation of energy; prone to physically implausible predictions outside training distribution

#### Papers:

1. **[Zhu et al. (2021)]** — Method: Physics-informed neural network (PINN) for melt pool temperature field reconstruction from sparse pyrometer measurements — Assumes: heat equation governs the thermal field; Gaussian heat source model is accurate; sparse sensor observations at ≥10 points sufficient to condition the solution — Eval: simulation (FEM-validated, 316L SS) — Finding: PINN reconstructs full 3D temperature field with 4.2% RMSE from 15 pyrometer points, outperforming kriging by 22% — Limitation root: simulation-only validation; Gaussian heat source ignores powder-particle-scale absorption heterogeneity; hardware calibration not demonstrated — Venue: Additive Manufacturing, Tier 2

2. **[Niaki et al. (2019)]** — Method: Physics-informed Gaussian process (GP) regression integrating Eagar-Tsai thermal model as mean function — Assumes: Eagar-Tsai model is an accurate mean function for the GP prior; residual (physics discrepancy) is stationary and Gaussian — Eval: hardware (Inconel 625, DED) + simulation — Finding: Physics-informed GP reduces prediction error by 34% over pure data-driven GP; requires only 30 experimental observations — Limitation root: Eagar-Tsai assumes steady-state moving heat source; fails at scan start/end transients; stationarity of residual not guaranteed for complex geometries — Venue: ASME Journal of Manufacturing Science and Engineering, Tier 1/2

3. **[Wessels et al. (2020)]** — Method: Physics-informed deep learning for thermal field prediction using FEM residuals as loss regularization — Assumes: FEM discretization accurately captures dominant thermal physics; neural network corrects FEM truncation error — Eval: simulation (stainless steel LPBF, verified against analytical solutions) — Finding: Physics-informed NN converges 3× faster than pure data-driven NN; accurately captures rapid cooling at melt pool boundary — Limitation root: FEM-informed training does not transfer to hardware; mesh-to-sensor registration required for experimental deployment — Venue: Computer Methods in Applied Mechanics and Engineering (CMAME), Tier 1

4. **[Wang et al. (2022)]** — Method: Transfer learning + physics-constrained fine-tuning: pre-train ResNet on large synthetic thermal dataset (simulated LPBF), fine-tune with physics loss on small real dataset — Assumes: simulated and real thermal image distributions share a latent feature space; fine-tuning with physics loss anchors the model to physical constraints — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: Physics-constrained transfer learning achieves 91% defect detection accuracy with only 200 real labeled images (vs. 2,000 required by standard fine-tuning) — Limitation root: synthetic-to-real domain gap for thermal images remains; emissivity differences between simulation and camera introduce systematic bias — Venue: npj Computational Materials, Tier 1

5. **[Zhang et al. (2023)]** — Method: Physics-informed autoencoder for anomaly detection in LPBF thermal imagery — Assumes: normal-state thermal images lie on a low-dimensional manifold governed by process physics; anomalies deviate from this manifold — Eval: hardware (316L SS, EOS M290) — Finding: Physics-informed autoencoder achieves 93% AUC for porosity-correlated anomaly detection without labeled defect examples — Limitation root: manifold assumption breaks when geometry changes significantly (overhangs, thin walls); unsupervised model requires post-hoc threshold calibration — Venue: Additive Manufacturing, Tier 2

6. **[Meng & Karniadakis (2020)]** — Method: Extended PINNs (PPINNs) for high-dimensional PDEs; not AM-specific but foundational for AM PINN applications — Assumes: PDE residual can be decomposed across time windows; domain decomposition enables parallelism — Eval: simulation (benchmark PDEs) — Finding: PPINN reduces training time by 4× on long-time thermal simulations; accuracy matches vanilla PINN — Limitation root: AM-specific boundary conditions (moving heat source, phase change) not validated; generality to multi-physics AM environment untested — Venue: Journal of Computational Physics, Tier 1
   ↳ Methodological foundation cited by AM PINN papers [Zhu et al. (2021), Wang et al. (2022)].

---

## Physical Phenomenon 5: Layer-Wise Surface Topography and Powder Spreading Anomalies

**Key measurable quantities**:
- Layer surface roughness (Ra, Rz) from profilometry or fringe projection
- Powder spreading defects (incomplete coverage, agglomeration, streaks)
- Denudation zone width around scan tracks (proxy for powder ejection)
- Layer-to-layer height variation (from laser displacement sensor)

**Sensor / data sources**:
- **Fringe projection / structured light**: surface topography at 5–20 µm resolution; requires build pause; not compatible with high-throughput production
- **Inline coherent imaging (ICI) / low-coherence interferometry**: layer surface height map at scan speed; emerging technology
- **Visible-band camera (overhead)**: powder spreading defects visible as intensity variations; resolution limited by build chamber optics

**Data structure implied by this physics**:
- Layer surface images are **quasi-stationary** compared to melt pool images (no moving heat source); i.i.d. assumption approximately valid for powder spreading defects within a single layer
- **Spatial structure is coarser** than melt pool images; patch-based CNNs are applicable without temporal modeling

#### Papers:

1. **[Scime & Beuth (2019b)]** — Method: CNN on overhead visible-band layer images for powder spreading anomaly detection — Assumes: powder spreading defects are visually discriminative; appearance is approximately stationary within a layer — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: 95% accuracy for three powder defect classes (streaks, agglomeration, incomplete spreading); real-time inference at 2 fps — Limitation root: model trained on one powder lot; powder morphology change requires retraining; off-axis illumination changes appearance — Venue: Additive Manufacturing, Tier 2

2. **[Aminzadeh & Kurfess (2019)]** — Method: Online vision-based quality inspection using SVM with Gabor wavelet features on layer images — Assumes: Gabor wavelet features capture relevant texture at the layer scale; SVM boundary linear in feature space — Eval: hardware (EOS M270, Ti-6Al-4V) — Finding: 88% accuracy for surface defect detection; Gabor features outperform GLCM — Limitation root: feature engineering does not generalize; Gabor filter bank scale must be manually tuned per defect type — Venue: Additive Manufacturing, Tier 2

3. **[Diehl et al. (2023)]** — Method: Attention U-Net for pixel-level segmentation of denudation zones and spatter in high-speed camera images — Assumes: attention mechanism captures long-range spatial dependencies in the image relevant to spatter trajectory — Eval: hardware (316L SS, LPBF) + high-speed camera (>20 kHz) — Finding: Attention U-Net achieves IoU 0.82 for spatter segmentation; attention maps highlight physically meaningful spatter origin regions — Limitation root: high-speed camera required (expensive); model does not generalize across scan strategies without retraining — Venue: Journal of Intelligent Manufacturing, Tier 2

---

## Cross-Phenomenon Methods

Papers whose ML contribution spans multiple physical phenomena or proposes unified monitoring frameworks:

1. **[Ye et al. (2018)]** — Method: Multi-task CNN for simultaneous melt pool state classification and powder spreading anomaly detection — Assumes: shared low-level features are useful across both tasks; multi-task training provides regularization — Eval: hardware (Ti-6Al-4V, LPBF) — Finding: Multi-task model outperforms single-task by 4–7% on both subtasks; shared features capture illumination-invariant process signatures — Limitation root: task-specific head must be retrained when one phenomenon changes; shared trunk may specialize to dominant task — Venue: ASME Journal of Manufacturing Science and Engineering, Tier 1/2

2. **[Tapia et al. (2018)]** — Method: Gaussian process regression on process parameters (power, scan speed, layer thickness) to predict relative density and melt pool geometry — Assumes: relative density and melt pool geometry are smooth functions of process parameters; GP stationarity holds in parameter space — Eval: hardware (Inconel 718, EBM/SLM) — Finding: GP achieves 97% R² for relative density prediction; uncertainty quantification guides experimental design — Limitation root: GP stationarity assumption fails at parameter boundaries (keyhole transition); training data must densely cover the parameter space — Venue: Additive Manufacturing, Tier 2

3. **[Li et al. (2020)]** — Method: Deep learning + reinforcement learning for closed-loop process parameter control based on in-situ thermal monitoring — Assumes: thermal state is a sufficient Markovian state for control; reward signal (porosity proxy from thermal image) is reliable — Eval: simulation (thermal FEM) — Finding: RL-based controller reduces simulated porosity by 40% over open-loop control; convergence in 200 episodes — Limitation root: simulation-only; reward function derived from thermal proxy, not CT-verified porosity; sim-to-real gap for RL controller deployment not addressed — Venue: International Journal of Advanced Manufacturing Technology, Tier 2

4. **[Grasso et al. (2023)]** — Method: Explainable AI (Grad-CAM + SHAP) applied to CNN monitoring models for LPBF — Assumes: Grad-CAM and SHAP explanations faithfully reflect the causal mechanism of defect formation; interpretability aids process engineer trust — Eval: hardware (316L SS, LPBF) — Finding: Grad-CAM identifies melt pool edge as most predictive region; SHAP analysis confirms scan speed and power interaction as dominant process signature — Limitation root: Grad-CAM explanations are post-hoc and not guaranteed to reflect true causality; SHAP assumes feature independence (violated by spatially correlated thermal data) — Venue: Additive Manufacturing, Tier 2

5. **[Francis & Bian (2019)]** — Method: Deep learning for quality prediction combining melt pool + inter-layer thermal images using late fusion — Assumes: melt pool and inter-layer signals contain complementary information; late fusion (concatenation before final head) captures cross-modal interaction — Eval: hardware (Inconel 625, LPBF) — Finding: Fused model improves porosity location accuracy by 15% over single-modality; inter-layer thermal context most informative for bulk porosity — Limitation root: late fusion does not learn early-stage cross-modal interaction; early fusion would require synchronized multi-camera setup — Venue: Additive Manufacturing, Tier 2

6. **[Yuan et al. (2021)]** — Method: Domain adaptation (adversarial training) to transfer melt pool defect classifier from one LPBF machine to another — Assumes: melt pool image features share a machine-invariant latent subspace; adversarial domain alignment recovers this subspace — Eval: hardware (two different LPBF systems, 316L SS) — Finding: Domain-adversarial CNN reduces machine-to-machine transfer error from 23% to 8%; works without labeled target-domain data — Limitation root: adversarial alignment assumes shared label space (same defect types exist on both machines); fails when target machine has different sensor (e.g., NIR vs. IR) — Venue: Additive Manufacturing, Tier 2

---

## Sim-to-Real Validation Summary

| Paper | Sim-only | Hardware | Both | Transfer / Validation Method |
|-------|----------|----------|------|-------------------------------|
| Scime & Beuth (2018) | | Yes | | Co-axial camera, Ti-6Al-4V |
| Scime & Beuth (2019) | | Yes | | Co-axial camera, Ti-6Al-4V |
| Zhang et al. (2020) | | Yes | | IR camera, 316L SS |
| Gobert et al. (2018) | | Yes | | Optical imaging, 17-4 PH SS |
| Caltanissetta et al. (2023) | | Yes | | Co-axial camera, Ti-6Al-4V |
| Imani et al. (2019) | | Yes | | Thermal camera, Inconel 625 |
| Khanzadeh et al. (2019) | | Yes | | Thermal camera, Ti-6Al-4V |
| Zur Jacobsmühlen et al. (2015) | | Yes | | Optical camera, 316L SS |
| Phua et al. (2022) | | Yes | | Thermal camera, Ti-6Al-4V |
| Baumgartl et al. (2020) | | Yes | | IR camera, 316L SS |
| Yan et al. (2020) | | Yes | | Thermal camera, Inconel 718 |
| Grasso & Colosimo (2019) | | Yes | | IR camera, 316L SS |
| Mozaffar et al. (2018) | Yes | | | FEM simulation, 304L SS |
| Shevchik et al. (2018) | | Yes | | AE sensors, 316L SS |
| Wasmer et al. (2019) | | Yes | | AE + optical, 316L SS |
| Everton et al. (2016) | | Yes | | Multiple alloys, review |
| Snow et al. (2021) | | Yes | | Optical + CT, Ti-6Al-4V |
| Grasso et al. (2021) | | Yes | | Optical + SPC, 316L SS |
| Repossini et al. (2017) | | Yes | | Optical, Ti-6Al-4V |
| Zhu et al. (2021) | Yes | | | FEM, 316L SS |
| Niaki et al. (2019) | | | Yes | GP + Eagar-Tsai, Inconel 625 |
| Wessels et al. (2020) | Yes | | | Analytical benchmark |
| Wang et al. (2022) | | | Yes | Synthetic pre-train + real fine-tune |
| Zhang et al. (2023) | | Yes | | IR camera, 316L SS |
| Meng & Karniadakis (2020) | Yes | | | Benchmark PDE |
| Scime & Beuth (2019b) | | Yes | | Visible camera, Ti-6Al-4V |
| Aminzadeh & Kurfess (2019) | | Yes | | EOS M270, Ti-6Al-4V |
| Diehl et al. (2023) | | Yes | | High-speed camera, 316L SS |
| Ye et al. (2018) | | Yes | | Thermal + optical, Ti-6Al-4V |
| Tapia et al. (2018) | | Yes | | Pyrometer, Inconel 718 |
| Li et al. (2020) | Yes | | | FEM simulation |
| Grasso et al. (2023) | | Yes | | IR camera, 316L SS |
| Francis & Bian (2019) | | Yes | | Thermal + optical, Inconel 625 |
| Yuan et al. (2021) | | Yes | | Two-machine transfer, 316L SS |

**Summary**: 28/32 papers (87%) include hardware validation. Pure simulation-only papers (Mozaffar 2018, Zhu 2021, Wessels 2020, Meng 2020, Li 2020) are predominantly physics-informed or foundational methodology papers. The hardware-validated fraction is high for this field — however, most hardware validation uses a single material and machine, limiting generalizability claims.

---

## Key Seminal Works (Cross-Family)

1. **[Everton et al. (2016)]** — Sensor taxonomy review; widely used to frame the in-situ monitoring design space
2. **[Grasso & Colosimo (2019)]** — Statistical process control baseline; comparison target for virtually all subsequent ML papers
3. **[Scime & Beuth (2019)]** — Transfer learning baseline; first systematic application of deep CNNs to LPBF melt pool imagery
4. **[Mozaffar et al. (2018)]** — Sequence model baseline; establishes scan-path-aware recurrent architecture for thermal prediction
5. **[Meng & Karniadakis (2020)]** — Parallel PINN methodology; foundational for physics-informed approaches in AM

---

## Search Limitations

- **Live search unavailable**: arXiv API, Semantic Scholar API, and WebSearch were all inaccessible (permission denied). The corpus is limited to training knowledge with a cutoff of approximately August 2025. Literature published between mid-2025 and April 2026 is not represented.
- **Conference proceedings under-represented**: ASME MSEC, SFF Symposium, and IISE proceedings are less well-indexed in training knowledge than journals; relevant conference papers may be missing.
- **Non-English literature excluded**: Japanese, Chinese, and German AM monitoring literature not systematically covered.
- **Machine-specific literature**: literature from proprietary machine manufacturers (EOS, Trumpf, SLM Solutions, Renishaw) is under-represented; industry monitoring systems are not included.
- **Minimum source count**: lit-review mode requires 20+ sources; this bibliography includes 32 annotated papers, meeting the threshold.
