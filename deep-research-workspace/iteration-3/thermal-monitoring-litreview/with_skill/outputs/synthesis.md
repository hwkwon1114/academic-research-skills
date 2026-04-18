# Synthesis Report
## Topic: Machine Learning for In-Situ Thermal Monitoring and Defect Detection in Laser Powder Bed Fusion

**Agent**: synthesis_agent (deep-research v3.0, lit-review mode)
**Date**: 2026-04-07
**Input corpus**: 32 papers from bibliography_agent (see bibliography.md)

---

> **Physics-to-Data Map**: As established in the bibliography's physics-first organization, LPBF involves five physical phenomena with qualitatively different data structures: (1) melt pool / solidification dynamics — non-stationary, spatially correlated, label-scarce; (2) inter-layer thermal accumulation — spatially structured, build-height dependent, multi-scale; (3) keyhole formation and porosity — rare/bursty events, multimodal signature, temporally sparse; (4) physics-informed approaches — label-scarce, governed by the heat equation; (5) layer-wise surface topography — quasi-stationary within a layer, coarser spatial structure. These data structure implications drive which ML families are viable, which is made explicit under each family below.

---

## Model-Family Landscape

### Family 1: Transfer-Learned CNNs (Discriminative Classifiers)

**Foundation paper**: Scime & Beuth (2019) — fine-tuned AlexNet on co-axial melt pool images
**Shared assumptions**:
1. Melt pool appearance is approximately stationary across build height (i.i.d. images)
2. ImageNet-pretrained features are transferable to thermal/NIR imagery
3. Defect classes are visually discriminable in single-frame 2D images
4. Sufficient labeled defect examples exist (hundreds to thousands)

**Papers in this family** (most constrained → most general):

1. **Most constrained — Scime & Beuth (2018)**: SVM on hand-crafted melt pool features (area, brightness, eccentricity). Manual feature engineering; linear classifier; no spatial context. Establishes the feature-engineering baseline.

2. **Scime & Beuth (2019)**: Fine-tuned AlexNet. Replaces manual features with learned convolutional features; still assumes single-frame stationarity. First to demonstrate >90% accuracy on three defect classes.

3. **Zhang et al. (2020)**: ResNet-50 fine-tuned on thermal images. Deeper architecture; attempts spatter-to-porosity correlation. Still single-frame; does not distinguish mechanistic origin of spatter.

4. **Gobert et al. (2018)**: Gradient-boosted trees on layer-averaged features. Trades spatial resolution for robustness; layer averaging is an explicit stationarity relaxation (within-layer, not across layers). Shows that spatial resolution is critical for pore localization.

5. **Phua et al. (2022)**: Vision Transformer (ViT) with attention. Relaxes the locality assumption of convolution — attention over image patches provides global context. Attention maps align with physically meaningful melt pool regions. Still requires fine-tuning from ImageNet ViT, introducing domain mismatch.

**Family-level ceiling**: The stationarity assumption (that a model trained on early-build images transfers to late-build images, or across different part geometries) limits all members of this family. Geometry-dependent thermal history changes the appearance distribution in a way that single-frame classifiers cannot handle. The ceiling is not a hardware ceiling — it is a statistical assumption ceiling. Breaking it requires either (a) conditioning the classifier on thermal history context (→ Family 2) or (b) embedding physical constraints (→ Family 4).

**Sim-to-real status**: All papers in this family are hardware-validated. No paper in this family makes cross-machine generalization claims with multi-machine evidence; Yuan et al. (2021) (cross-family) addresses this via domain adaptation.

---

### Family 2: Temporal and Sequence-Aware Models

**Foundation paper**: Mozaffar et al. (2018) — LSTM on scan path history for melt pool geometry prediction
**Shared assumptions**:
1. Process state evolves as a temporally structured sequence; current state depends on recent history
2. The LSTM hidden state is a sufficient summary of relevant history (finite-memory Markov approximation)
3. Scan path is the primary state variable (or thermal image sequence is a sufficient proxy for thermal history)

**Papers in this family** (most constrained → most general):

1. **Most constrained — Mozaffar et al. (2018)**: LSTM on scan path + process parameters to predict melt pool geometry. Simulation-only validation. Demonstrates that thermal memory effects are predictable from scan history but does not validate on hardware.

2. **Yan et al. (2020)**: LSTM + CNN hybrid on 5-layer thermal image sequences. Hardware-validated (Inconel 718). Adding spatial context (CNN) to the temporal model captures the inter-layer thermal accumulation effect missing in Family 1. 8% improvement over single-frame CNN confirms that inter-layer history matters.

3. **Li et al. (2020)**: Deep RL + CNN for closed-loop process control using thermal feedback. Frames monitoring as a control problem (the most general use of temporal models). Simulation-only; demonstrates that LSTM-based control is conceptually feasible but the sim-to-real gap for RL is the largest in this corpus.

**Family-level ceiling**: The LSTM hidden state is a lossy summary. In LPBF, thermal history depends on the full 3D geometry of previously deposited layers — the LSTM cannot encode this spatial structure in its hidden state without prohibitively long sequences. The ceiling is the finite-memory bottleneck: LSTM cannot represent non-local spatial dependencies in the thermal field that influence current melt pool state.

**Sim-to-real status**: Mozaffar (2018) and Li (2020) are simulation-only. Yan (2020) is hardware-validated. The sim-to-real gap for temporal models is primarily the thermal boundary condition mismatch: FEM models assume known powder absorption, but hardware absorption varies with powder layer thickness and laser conditioning.

---

### Family 3: Spatial Segmentation Models (Encoder-Decoder / U-Net Variants)

**Foundation paper**: Caltanissetta et al. (2023) — U-Net for melt pool boundary segmentation
**Shared assumptions**:
1. Pixel-level labels are available (expensive but obtainable)
2. The decoder can recover spatial resolution from the bottleneck for fine-grained localization
3. Skip connections preserve high-frequency spatial detail needed for boundary delineation
4. Training distribution covers the relevant geometric configurations

**Papers in this family**:

1. **Caltanissetta et al. (2023)**: U-Net for melt pool boundary segmentation. Establishes pixel-level spatial accuracy (IoU 0.87); demonstrates that boundary area correlates with porosity events.

2. **Diehl et al. (2023)**: Attention U-Net for spatter and denudation zone segmentation. Extends U-Net with channel attention; attention gates focus on physically relevant regions. Requires high-speed camera (>20 kHz), limiting practical deployment.

**Family-level ceiling**: Pixel-level annotation cost is the primary ceiling. CT-verified pore locations cannot be registered to in-situ images without careful geometric calibration — the ground truth is inherently 3D while the model is 2D. The encoder-decoder architecture also cannot naturally model the temporal evolution of the melt pool boundary (→ this motivates combining Family 2 and Family 3 into a video segmentation approach, which has not been done in this corpus).

**Sim-to-real status**: Both papers are hardware-validated. Annotation pipeline for pixel-level labels is the sim-to-real barrier, not the model itself.

---

### Family 4: Physics-Informed Neural Networks and Physics-Constrained Learning

**Foundation paper**: Zhu et al. (2021) — PINN for temperature field reconstruction from sparse pyrometer data; methodologically grounded in Meng & Karniadakis (2020)
**Shared assumptions**:
1. The heat equation (or a simplified version thereof) accurately describes the dominant thermal physics
2. Physics residuals are differentiable and can be used as a soft training loss
3. Collocation points can be sampled in the domain where the PDE holds
4. The neural network has sufficient capacity to fit both the data loss and the physics loss simultaneously

**Papers in this family** (most constrained → most general):

1. **Most constrained — Meng & Karniadakis (2020)**: Parallel PINNs for general PDEs; simulation-only; not AM-specific. Establishes the decomposition strategy that enables training on long-time thermal simulations.

2. **Wessels et al. (2020)**: Physics-informed deep learning with FEM residuals for thermal field prediction. Simulation-validated; FEM provides coarse solution, NN corrects residual. Most conservative physics integration (FEM-informed, not fully PINN).

3. **Zhu et al. (2021)**: PINN for temperature field reconstruction from sparse sensors. Directly embeds the heat equation; achieves accurate reconstruction from 15 pyrometer points. Simulation-only; demonstrates feasibility of physics-informed sparse reconstruction.

4. **Niaki et al. (2019)**: Physics-informed GP with Eagar-Tsai model as prior mean. Straddles Family 4 and the GP baseline — uses GP uncertainty framework (interpretable, well-calibrated uncertainty) with physics prior. Hardware-validated on DED (not LPBF); demonstrates 34% error reduction over pure data-driven GP.

5. **Zhang et al. (2023)**: Physics-informed autoencoder for unsupervised anomaly detection. Relaxes the need for defect labels entirely by encoding the physics-consistent manifold; anomalies are off-manifold. Hardware-validated. Most practically deployable member of this family (no labeled defects required).

6. **Wang et al. (2022)**: Physics-constrained transfer learning — synthetic pre-training + physics-regularized fine-tuning. Bridges Families 1 and 4: CNN architecture from Family 1, but physics loss constrains the fine-tuned model. Achieves Family 1 accuracy with 10× less labeled hardware data. Most general member: combines simulation pre-training, transfer learning, and physics constraints.

**Family-level ceiling**: The governing-equation accuracy ceiling. LPBF thermal physics involves multi-physics interactions (fluid dynamics of the melt pool, evaporation, phase change, powder-scale heterogeneity) that the simplified heat equation does not capture. PINNs trained with the simplified heat equation will have systematic error wherever fluid dynamics and evaporation are important (i.e., in the keyhole regime). Additionally, the physics residual and the data loss have competing gradients during training — balancing these weights remains empirically driven, not principled.

**Sim-to-real status**: Meng (2020), Wessels (2020), and Zhu (2021) are simulation-only. Niaki (2019) and Wang (2022) are hardware-validated with transfer strategies. Zhang (2023) is hardware-validated without a simulation component. The family as a whole has the largest simulation-only fraction in this corpus — physics-informed methods are easier to validate in simulation (where the governing equation is exact by construction) than on hardware (where it is only approximate).

---

### Family 5: Acoustic and Multimodal Sensor Fusion

**Foundation paper**: Shevchik et al. (2018) — 1D CNN on acoustic emission for keyhole/pore classification
**Shared assumptions**:
1. Acoustic signatures of defect formation are temporally structured and discriminative
2. Sensor fusion provides complementary information that single-modality classifiers miss
3. Time-synchronized acquisition across modalities is achievable
4. Point AE sensor placement is sufficient for classification (no spatial resolution needed from acoustic modality)

**Papers in this family**:

1. **Shevchik et al. (2018)**: 1D CNN on raw AE waveforms. Establishes acoustic modality baseline; AUC 0.94 for keyhole vs. lack-of-fusion without any image data. Demonstrates that temporal structure in AE waveforms is discriminative.

2. **Wasmer et al. (2019)**: AE + optical emission fusion CNN. Demonstrates that the two modalities are complementary: optical alone misses subsurface pores that AE detects. Establishes multimodal fusion as the preferred architecture for keyhole detection.

**Family-level ceiling**: Spatial resolution. The AE sensor provides no position information; it can detect that a pore formed but not where in the layer. The ceiling is the physics of acoustic wave propagation — recovering the pore location from an AE signal requires either a sensor array (beamforming) or a model of wave propagation through the part, neither of which is in this corpus.

**Sim-to-real status**: Both papers are hardware-validated (316L SS LPBF). This is the most hardware-grounded family, but also the most limited to single-material single-machine validation.

---

### Family 6: Unsupervised and Statistical Process Control Methods

**Foundation paper**: Grasso & Colosimo (2019) — SPC + PCA on layer-wise thermal maps
**Shared assumptions**:
1. Normal process state produces observations from a stationary multivariate Gaussian distribution
2. Linear dimensionality reduction (PCA) is sufficient to capture the dominant variation modes
3. Deviations from the normal-state manifold are detectable by control chart logic
4. Expert labels are not required for deployment (unsupervised)

**Papers in this family**:

1. **Grasso & Colosimo (2019)**: SPC + PCA baseline. Pre-deep-learning; widely cited as the comparison target for supervised ML papers. 91% sensitivity for thermal anomaly detection.

2. **Khanzadeh et al. (2019)**: Self-organizing map clustering on thermal features. Unsupervised; identifies pore-correlated regions without defect labels. Less accurate than supervised CNNs but deployable without annotation.

3. **Zhang et al. (2023)**: Physics-informed autoencoder (also listed in Family 4). Bridges Family 6 (unsupervised anomaly detection) and Family 4 (physics constraints). The physics constraint tightens the normal-state manifold, reducing false positives.

4. **Grasso et al. (2023)**: Explainable AI (Grad-CAM + SHAP) applied to CNN monitors. Attempts to re-introduce interpretability (a strength of Family 6) into deep-learning models (Family 1). Demonstrates that CNN predictions align with physically meaningful regions but that SHAP feature independence assumption is violated.

**Family-level ceiling**: The Gaussian/linearity assumptions are violated during process transitions (parameter changes, overhang features, support structure boundaries). SPC-based methods systematically generate false alarms at geometric transitions because the thermal distribution is non-Gaussian in these regions.

**Sim-to-real status**: All papers hardware-validated. This family has no simulation-only papers — unsupervised methods do not require simulation data.

---

## Cross-Family Relationships

| Families | Relationship Type | Description |
|----------|------------------|-------------|
| Family 1 (Transfer CNN) ↔ Family 2 (Temporal) | Composable | Adding temporal context (Family 2) to spatial feature extraction (Family 1) is the natural extension; Yan (2020) combines them. The cost is increased data and training complexity. |
| Family 1 (Transfer CNN) ↔ Family 4 (PINN) | Composable | Physics-constrained transfer learning [Wang 2022] fuses these families. Physics loss replaces some of the labeled data requirement; the CNN architecture is preserved. |
| Family 4 (PINN) ↔ Family 6 (Unsupervised) | Composable | Physics-informed autoencoder [Zhang 2023] achieves unsupervised anomaly detection (Family 6 goal) with physics-consistent manifold (Family 4 mechanism). This is the most productive fusion in the corpus. |
| Family 1 (Transfer CNN) ↔ Family 5 (Acoustic Fusion) | Composable | Late-fusion or early-fusion of optical CNN features with acoustic CNN features [Wasmer 2019; Francis & Bian 2019]. Complementary modalities; practical barrier is time-synchronization hardware. |
| Family 3 (U-Net Segmentation) ↔ Family 2 (Temporal) | Gap (unexplored) | Video segmentation combining temporal sequence modeling with pixel-level spatial output would address both the non-stationarity problem (Family 1 ceiling) and the localization problem (Family 3 strength). No paper in this corpus combines them. |
| Family 1 (Transfer CNN) ↔ Family 6 (SPC) | Tradeoff | CNNs outperform SPC on accuracy but sacrifice interpretability and require labeled defect data. SPC deploys without labels but fails on non-Gaussian transitions. The choice between them is a label-availability and interpretability tradeoff. |
| Family 2 (Temporal LSTM) ↔ Family 4 (PINN) | Incompatible (current) | LSTM models the thermal history as a latent sequence; PINN models it as a PDE solution. These encode the same physics in fundamentally different ways. Combining them (PDE-constrained LSTM) would require differentiable physics integration into the recurrent update — not yet demonstrated in this corpus. |

---

## Sim-to-Real Gap Summary

- **Physics-informed methods (Family 4) have the largest sim-to-real gap**: Zhu (2021), Wessels (2020), and Meng (2020) are simulation-only. The core issue is that the physics embedded in the PINN (simplified heat equation) is exact in simulation by construction but only approximate on hardware — emissivity uncertainty, powder-absorption heterogeneity, and melt pool fluid dynamics are not in the simplified governing equation.

- **Hardware-validated families lack cross-machine evidence**: Families 1, 5, and 6 are almost entirely hardware-validated but on single-machine, single-material setups. Yuan (2021) is the only paper demonstrating machine-to-machine transfer, and only for the same material (316L SS) and defect types. No paper demonstrates cross-material and cross-machine generalization simultaneously.

- **Simulation-to-hardware transfer strategies are underexplored**: Wang (2022) is the only paper that systematically addresses the synthetic-to-real domain gap for thermal imagery (physics-constrained fine-tuning). No paper in the corpus uses domain randomization (a strategy common in robotics sim-to-real) for AM thermal monitoring. This gap is both a research opportunity and a practical barrier to deploying physics-informed methods on production machines.

- **RL-based control (Li 2020) has the largest deployment gap**: Simulation-only; the RL reward function uses a thermal proxy for porosity that has not been calibrated against CT ground truth. The behavioral gap between the simulated and real thermal response is compounded by the policy's sensitivity to reward signal accuracy.

---

## Assumption-Driven Limitation Map

| Limitation | Root Assumption | Papers Affected | Relaxation Attempted? |
|------------|----------------|-----------------|----------------------|
| Model accuracy degrades across build height (layer drift) | Stationarity of melt pool appearance (Family 1) | Scime 2018/2019, Zhang 2020, Baumgartl 2020, Gobert 2018 | Partial: Yan (2020) adds LSTM history; Yuan (2021) adds domain adaptation |
| Cannot localize pore position (only classify) | Point sensor / single-frame classification without spatial output (Families 1, 5, 6) | Shevchik 2018, Wasmer 2019, Khanzadeh 2019, Snow 2021 | Yes: U-Net segmentation (Family 3) provides spatial localization |
| Fails at geometric transitions (overhangs, support structures) | Gaussian / stationarity assumption of normal-state distribution (Family 6) | Grasso 2019, SPC approaches | Partial: CNN features replace PCA (Grasso 2021) but Gaussian control chart retained |
| High label cost for supervised training | Availability of CT-verified, spatially registered defect labels | All Family 1 and Family 3 papers | Yes: physics-informed autoencoder (Zhang 2023) eliminates label requirement; active learning not yet explored |
| PINN fails in keyhole regime | Simplified heat equation omits fluid dynamics and evaporation | Zhu 2021, Wessels 2020 | No: no paper extends PINN to include melt pool fluid dynamics |
| LSTM hidden state loses early-layer thermal history | Finite-memory Markov approximation of thermal history | Mozaffar 2018, Yan 2020 | Partial: 3D CNN on volumetric stacks (Imani 2019) captures more history but not infinite history |
| No spatial resolution from acoustic sensor | Point sensor assumption (Family 5) | Shevchik 2018, Wasmer 2019 | No: no paper implements acoustic sensor arrays for spatial localization |
| Poor generalization across materials | Training data from single material; emissivity and thermal properties are material-specific | All hardware-validated papers | Partial: domain adaptation (Yuan 2021) addresses machine-to-machine but not material-to-material |
| Physics-to-hardware gap for PINNs | Simplified physics (heat equation only) vs. multi-physics reality | Zhu 2021, Wessels 2020, Niaki 2019 | Partial: Niaki (2019) calibrates Eagar-Tsai mean function from hardware data; full multi-physics PINN not attempted |

---

## Knowledge Gaps (Priority-Ordered)

1. **Cross-machine, cross-material generalization** — Transfer gap
   - Missing: No paper demonstrates that a melt pool defect classifier trained on machine A with material X can be deployed on machine B with material Y without retraining. — Closest papers: Yuan (2021) for machine-to-machine; Niaki (2019) for material-specific physics calibration. — Matters because: production AM uses multiple machines and materials; retraining from scratch for every configuration is economically impractical.

2. **Temporal segmentation: combining U-Net spatial output with sequence-aware input** — Composition gap
   - Missing: No paper applies video segmentation (pixel-level sequence modeling, e.g., temporal U-Net, ConvLSTM encoder-decoder) to melt pool in-situ data. — Closest papers: Yan (2020) for temporal modeling; Caltanissetta (2023) for spatial segmentation; Diehl (2023) for attention segmentation. — Matters because: the non-stationarity problem (Family 1 ceiling) and the localization problem (Family 3 ceiling) are jointly solved by video segmentation, yet no paper combines them.

3. **Hardware-validated physics-informed methods for keyhole detection** — Transfer gap + assumption gap
   - Missing: All papers that embed the heat equation (Zhu 2021, Wessels 2020, Meng 2020) are simulation-only or use DED (Niaki 2019). No hardware-validated PINN for LPBF keyhole porosity detection exists in this corpus. — Closest papers: Wang (2022) for physics-constrained transfer; Zhang (2023) for hardware-validated physics-informed autoencoder (but not keyhole-specific). — Matters because: keyhole porosity is the dominant defect mode in high-power LPBF; a physics-informed approach that generalizes with few labels would be a significant practical advance.

4. **Acoustic sensor array for pore localization** — Scale gap + representation gap
   - Missing: All acoustic papers use a single-point AE sensor. No paper demonstrates localization of acoustic emission sources within a layer using an array or beamforming approach. — Closest papers: Shevchik (2018), Wasmer (2019). — Matters because: binary "pore/no pore" classification is insufficient for closed-loop correction; spatial location is needed to trigger targeted parameter adjustment.

5. **Active learning for labeled defect dataset construction** — Assumption gap
   - Missing: No paper uses active learning to reduce the annotation cost for supervised CNN training. All Family 1 papers assume a fixed labeled dataset; none use uncertainty-guided sample selection to minimize CT-validation cost. — Closest papers: Tapia (2018) for GP-based uncertainty-guided process design; Zhang (2023) for unsupervised approach avoiding labels. — Matters because: label cost is the primary barrier to deploying supervised CNN methods in production; active learning directly addresses this bottleneck.

6. **Multi-physics PINN incorporating melt pool fluid dynamics** — Assumption gap
   - Missing: All PINN papers use the simplified heat equation. Melt pool fluid dynamics (Marangoni flow, vapor recoil pressure) are the dominant mechanism in keyhole formation, but no PINN includes them. — Closest papers: Zhu (2021), Wessels (2020). — Matters because: a PINN that only embeds the heat equation will systematically fail to predict keyhole formation, which is the most important defect in high-power LPBF.

7. **Real-time inference constraints under production throughput** — Scale gap
   - Missing: No paper reports inference latency against the scan speed constraint (typical LPBF scan speed 0.5–1.5 m/s; melt pool residence time ~1 ms). Most papers report accuracy but not whether inference can operate in closed-loop at scan speed. — Closest papers: Scime & Beuth (2019b) report 2 fps for layer-level classification (insufficient for scan-level closed-loop). — Matters because: an accurate but too-slow model cannot close the feedback loop for real-time process correction.

---

## Synthesis Limitations

- Live search unavailable: this synthesis is limited to training knowledge (~August 2025 cutoff). Papers published between mid-2025 and April 2026 are not included; the field is active and this review is likely incomplete for the most recent 9 months.
- Single-material dominance: 316L SS and Ti-6Al-4V dominate the hardware-validated corpus; results for Inconel, aluminum alloys, and copper-based alloys are under-represented.
- Non-English literature excluded: Japanese and Chinese AM monitoring literature (significant in industrial contexts) is not covered.
- Conference papers under-represented: SFF Symposium and ASME MSEC proceedings are primary venues for early-stage LPBF monitoring research but are less well-indexed in training knowledge.
- Industry systems excluded: commercial monitoring systems (e.g., EOS EOSTATE MeltPool, SLM Solutions QM Meltpool 3D, Renishaw InfiniAM) are not covered; only academic research is included.
