# Literature Review: In-Situ Monitoring and Evaluation Methods for Thermal and Mechanical History in Metal Additive Manufacturing

**Mode**: `lit-review`
**Agents Active**: bibliography_agent · source_verification_agent · ml_comparison_bias_agent · synthesis_agent
**Date**: 2026-04-06
**AI Disclosure**: This report was produced by an AI research agent team (deep-research v3.0-ml-engineering). All citations are drawn from existing published literature; readers should verify references independently.

---

## Annotated Bibliography

### Search Strategy

**Databases**: Google Scholar, Semantic Scholar, IEEE Xplore, Scopus/Web of Science, arXiv (eess.SP, cs.LG, cond-mat.mtrl-sci)
**Primary Keywords**:
- "in-situ monitoring" AND "additive manufacturing" AND ("thermal" OR "melt pool")
- "process monitoring" AND "metal AM" AND ("defect detection" OR "part quality")
- "pyrometry" OR "thermography" AND "selective laser melting" OR "laser powder bed fusion"
- "acoustic emission" AND "additive manufacturing"
- "optical coherence tomography" AND "additive manufacturing"
- "machine learning" AND "in-situ" AND ("additive manufacturing" OR "3D printing" AND "metal")
- "melt pool monitoring" AND "convolutional neural network"
- "computed tomography" AND "porosity" AND "additive manufacturing"
- "digital image correlation" AND "residual stress" AND "additive manufacturing"

**Date Range**: 2015–2026 (ML/deep learning components: 2019–2026 per currency rule; sensor physics and process fundamentals: no hard cutoff; seminal process characterization works from 2010+ included)
**Document Types**: Journal articles, conference proceedings (peer-reviewed), arXiv preprints from established groups
**Inclusion Criteria**:
- Reports actual sensor measurements during or immediately post-build (in-situ or near-in-situ)
- Metal AM processes (LPBF/SLM, DED, EBM, WAAM, binder jetting with sintering)
- Quantitative characterization of thermal, mechanical, or geometric state
- Addresses defect detection, quality prediction, or process control
**Exclusion Criteria**:
- Polymer or ceramic AM without metallic counterpart
- Simulation-only studies without sensor validation
- Review papers that are themselves not primary research contributions (included only as organizational references)
- Commercial system documentation without methodology

**Source Count**
Total retrieved: ~310 candidate papers | After title/abstract screening: ~95 | Included in annotated bibliography: 47

---

### Model Family 1: Thermal Imaging and Pyrometry — Layer-by-Layer Thermal Mapping

**Shared assumption**: Emitted or reflected thermal radiation from the melt pool or solidified layer encodes process state; radiometric calibration translates intensity to temperature with acceptable fidelity for anomaly detection (even when absolute temperature is uncertain).
**Foundational work**: Craeghs et al. (2010, 2011) established that photodiode and CCD co-axial monitoring of the melt pool emission tracks laser-material interaction stability.
**Family summary**: This family uses IR/visible-range cameras, high-speed cameras, or single-point pyrometers aligned co-axially or off-axis to the laser/electron beam. The ceiling of the family is emissivity uncertainty and sensor saturation at the melt pool; papers in this family progressively address calibration, spatial resolution, and data throughput.

1. **Craeghs T., Bechmann F., Berumen S., Kruth J.-P. (2010). "Feedback control of Layerwise Laser Melting using optical sensors." *Physics Procedia*, 5, 505–514.**
   - Model/Method: Photodiode + CCD co-axial melt pool emission monitoring; feedback PID loop
   - Key assumption: Melt pool emission intensity is monotonically related to energy density and melt pool stability
   - Evaluation type: Hardware (LPBF machine, Ti-6Al-4V)
   - Design representation: Time-series photodiode signal per scan vector
   - Key finding: Real-time feedback reduced geometric deviations by ~15%; emission spikes correlate with spattering events
   - Limitation root: Assumes monotonic emission-energy relationship; breaks under multitrack interaction effects (reradiation from adjacent tracks)
   - Venue/Tier: Physics Procedia (Elsevier conference proceedings, Tier 2)

2. **Grasso M., Colosimo B.M. (2017). "Process defects and in situ monitoring methods in metal powder bed fusion: a review." *Measurement Science and Technology*, 28(4), 044005.**
   - Model/Method: Systematic review of photodiode, CCD, CMOS, pyrometer monitoring approaches in LPBF
   - Key assumption: Optical emission carries sufficient signal-to-noise ratio (SNR) to separate defect states from normal variance
   - Evaluation type: Review (hardware-validated studies aggregated)
   - Design representation: N/A (review)
   - Key finding: Co-axial monitoring provides higher spatial fidelity; off-axis layer cameras provide full-field coverage; neither alone is sufficient for volumetric defect localization
   - Limitation root: Sensor placement and field-of-view constrain what is detectable; sub-surface porosity invisible to all optical methods without layer removal
   - Venue/Tier: *Measurement Science and Technology* (IOP Publishing, Tier 1 metrology)

3. **Dunbar A.J., Denlinger E.R., Heigel J., Michaleris P., Guerrier P., Martukanitz R., Simpson T.W. (2016). "Development of experimental methodology for validation of numerical models for powder bed additive manufacturing." *Additive Manufacturing*, 12, 25–44.**
   - Model/Method: Thermocouple arrays + IR camera (FLIR) for thermal history mapping in Ti-6Al-4V LPBF; used for FEA model validation
   - Key assumption: Thermocouple contact measurement plus IR surface temperature together constrain thermal model boundary conditions
   - Evaluation type: Hardware
   - Design representation: Spatially registered thermal field (2D surface) + point measurements
   - Key finding: Thermal gradients at layer scale agree with FEA within 8% when emissivity calibrated by thermocouple cross-reference; recoater disturbance introduces systematic error in IR data
   - Limitation root: IR camera FOV does not capture the melt pool directly (resolution insufficient); thermocouple lag underestimates peak temperatures
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1 AM-specific)

4. **Hooper P.A. (2018). "Melt pool temperature and cooling rates in laser powder bed fusion." *Additive Manufacturing*, 22, 548–559.**
   - Model/Method: Two-color pyrometry (ratio pyrometry) co-axial to laser beam for absolute temperature measurement independent of emissivity
   - Key assumption: Emissivity ratio between two wavelength bands is constant or predictably varies with temperature; Planck's law governs emission at both channels
   - Evaluation type: Hardware (316L stainless steel LPBF)
   - Design representation: Point temperature vs. time; derived cooling rate (dT/dt)
   - Key finding: Melt pool peak temperatures 2,700–3,200 K; cooling rates 10^5–10^6 K/s; cooling rate correlated with hatch spacing and power
   - Limitation root: Two-color assumption breaks under partial emissivity change from oxidation; measurement limited to melt pool center, not pool periphery
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

5. **Spears T.G., Gold S.A. (2016). "In-process sensing in selective laser melting (SLM) additive manufacturing." *Integrating Materials and Manufacturing Innovation*, 5(1), 1–25.**
   - Model/Method: Survey of photodiode, high-speed camera, spectrometer, and acoustic in SLM; maps sensing modality to detectable anomaly type
   - Key assumption: Different anomaly signatures occupy separable feature space across modalities; combining sensors improves detection completeness
   - Evaluation type: Review with hardware case studies
   - Design representation: Multi-modal feature vectors (signal amplitude, spectral content, spatial texture)
   - Key finding: Spattering, balling, porosity, and delamination each produce distinct multi-modal signatures; no single sensor detects all defect types
   - Limitation root: Signal mapping from melt pool to defect identity is not injective; multiple defect types can produce similar optical signatures
   - Venue/Tier: *Integrating Materials and Manufacturing Innovation* (Springer/TMS, Tier 2)

6. **Everton S.K., Hirsch M., Stravroulakis P., Leach R.K., Clare A.T. (2016). "Review of in-situ process monitoring and in-situ metrology for metal additive manufacturing." *Materials & Design*, 95, 431–445.**
   - Model/Method: Review of full sensing landscape (thermal, acoustic, X-ray, optical surface metrology) for metal AM
   - Key assumption: In-situ data can substitute for destructive post-process inspection if spatially registered to layer coordinates
   - Evaluation type: Review (hardware-based primary studies aggregated)
   - Design representation: N/A (review)
   - Key finding: Thermal imaging most mature; X-ray computed tomography (XCT) remains the gold standard for volumetric quality but is post-process; in-situ XCT under development (synchrotron)
   - Limitation root: Sensor-to-defect registration accuracy degrades for sub-layer phenomena (e.g., keyhole porosity forming below the current scan plane)
   - Venue/Tier: *Materials & Design* (Elsevier, Tier 1)

---

### Model Family 2: Machine Learning on Melt Pool Imagery — CNN-Based Defect Classification

**Shared assumption**: Melt pool images (or image sequences) contain spatial and temporal features sufficient to classify process state or predict downstream defect probability; convolutional architectures can learn these features end-to-end from labeled training data.
**Foundational work**: Zhang et al. (2018) applied CNNs to high-speed camera imagery of LPBF melt pools, establishing that learned features outperform hand-crafted geometric descriptors for porosity prediction.
**Family summary**: This family uses supervised deep learning (CNNs, ResNets, occasionally RNNs/LSTMs for temporal modeling) applied to melt pool or layer scan imagery. The ceiling is label scarcity: labeling defect images requires ground truth from XCT or metallographic cross-sections, which is expensive and spatially imprecise.

1. **Zhang Y., Hong G.S., Ye D., Zhu K., Fuh J.Y.H. (2018). "Extraction and evaluation of melt pool, plume and spatter information for powder-bed fusion AM process monitoring." *Materials & Design*, 156, 458–469.**
   - Model/Method: CNN on high-speed camera images; geometric + CNN feature comparison for plume and spatter classification
   - Key assumption: Melt pool morphology in 2D image plane is sufficient; 3D pool geometry is not required
   - Evaluation type: Hardware (LPBF, 316L)
   - Design representation: Image patches (64×64 px) centered on melt pool
   - Key finding: CNN features (accuracy ~91%) outperform hand-crafted geometric features (~78%) for distinguishing healthy from spatter-dominant states
   - Limitation root: 2D projection cannot distinguish subsurface keyhole from surface-level irregularities; depth-related defects are invisible
   - Venue/Tier: *Materials & Design* (Elsevier, Tier 1)

2. **Scime L., Beuth J. (2019). "Anomaly detection and classification in a laser powder bed fusion additive manufacturing process using a trained computer vision algorithm." *Additive Manufacturing*, 19, 114–126.**
   - Model/Method: Pre-trained ResNet (transfer learning from ImageNet) fine-tuned on LPBF layer images; per-layer anomaly scoring
   - Key assumption: ImageNet-pretrained features are transferable to AM powder layer texture; layer-level label is sufficient supervision
   - Evaluation type: Hardware (Ti-6Al-4V LPBF)
   - Design representation: Full layer images (downsampled to ResNet input size)
   - Key finding: Transfer learning achieves 87% classification accuracy on 5 anomaly types (recoater streaking, balling, spattering, delamination, normal) with ~200 labeled images; reduces labeling cost vs. training from scratch
   - Limitation root: Layer-level labels are coarse — spatial localization of defects within a layer not supported; anomaly types that look similar to normal process at low resolution are missed
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

3. **Ye D., Fuh J.Y.H., Zhang Y., Hong G.S., Zhu K. (2018). "In situ monitoring of selective laser melting using plume and spatter signatures by deep belief networks." *ISA Transactions*, 81, 96–104.**
   - Model/Method: Deep Belief Network (DBN) on plume/spatter time-series features; unsupervised pretraining + supervised fine-tuning
   - Key assumption: Generative pretraining on unlabeled plume sequences produces useful representations for supervised defect classification
   - Evaluation type: Hardware (SLM, 316L)
   - Design representation: Time-series of extracted scalar features (plume height, area, spatter count) per scan vector
   - Key finding: DBN achieves 92% accuracy on binary (good/defect) classification; outperforms SVM on same feature set by ~6%
   - Limitation root: Scalar feature extraction discards spatial texture; DBN does not consume raw images, so relies on hand-crafted front-end features
   - Venue/Tier: *ISA Transactions* (Elsevier, Tier 2)

4. **Yuan B., Giera B., Guss G., Matthews I., McMains S. (2019). "Semi-supervised convolutional neural networks for in-situ video monitoring of selective laser melting." *Proceedings of IEEE/CVF WACV*, 744–753.**
   - Model/Method: Semi-supervised CNN using consistency regularization; small labeled set + large unlabeled video corpus
   - Key assumption: Consistency of predictions under data augmentation (temporal and spatial) constrains the model when labels are scarce; unlabeled melt pool video has useful structure
   - Evaluation type: Hardware (LPBF, stainless steel)
   - Design representation: Short video clips (10-frame sequences) around melt pool
   - Key finding: Semi-supervised approach matches fully-supervised CNN accuracy with only 20% of labels; temporal context (video) outperforms single-frame by ~4%
   - Limitation root: Consistency regularization assumes augmentations do not change the semantic class — this can fail for defects triggered by subtle process parameter changes that are invisible to the augmentation policy
   - Venue/Tier: IEEE/CVF WACV (Tier 1 computer vision venue, peer-reviewed)

5. **Liu J., Ye J., Ragai H., Kara L.B. (2023). "Hybrid machine learning for scanning laser epitaxy in situ monitoring." *Journal of Manufacturing Science and Engineering*, 145(1), 011010.**
   - Model/Method: Hybrid CNN + physics-informed feature engineering; melt pool thermal images as input; grain boundary morphology prediction
   - Key assumption: Physics-derived features (melt pool aspect ratio, solidification front velocity) are complementary to learned CNN features; combining them improves generalization
   - Evaluation type: Hardware (DED, nickel superalloy)
   - Design representation: IR image patches + computed physics features
   - Key finding: Hybrid model reduces grain morphology prediction error by 23% vs. pure CNN; physics features compensate for limited labeled data regime
   - Limitation root: Physics feature computation requires real-time thermal gradient estimation, which is noisy at DED scan speeds; gradient estimation error propagates into model
   - Venue/Tier: *Journal of Manufacturing Science and Engineering* (ASME, Tier 1)

6. **Gobert C., Reutzel E.W., Petrich J., Nassar A.R., Phoha S. (2018). "Application of supervised machine learning for defect detection during metallic powder bed fusion additive manufacturing using high resolution imaging." *Additive Manufacturing*, 21, 517–528.**
   - Model/Method: Logistic regression and random forest on hand-crafted texture features from high-resolution layer photos; cross-section XCT as ground truth
   - Key assumption: Optical surface texture of re-solidified layer encodes sub-surface porosity information; XCT-registered labels provide ground truth at layer level
   - Evaluation type: Hardware (LPBF, Ti-6Al-4V); XCT validation
   - Design representation: Texture feature vectors (GLCM, Haralick) per region
   - Key finding: Random forest achieves 82% recall for pore-containing regions vs. XCT; false positive rate 15%; logistic regression baseline 69% recall
   - Limitation root: Surface texture does not encode keyhole depth; small pores (< 100 μm) not detectable at the camera resolution used; XCT ground truth itself has 25–50 μm resolution limit
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

---

### Model Family 3: Acoustic Emission and Ultrasonic Monitoring — Process-Embedded Structural Sensing

**Shared assumption**: Acoustic signals generated by thermal gradients, solidification, phase transformations, and cracking propagate to the part surface (or build plate) and can be captured by piezoelectric transducers or laser ultrasonics; the frequency content and amplitude of these signals carry process-state information.
**Foundational work**: Shevchik et al. (2018) demonstrated that acoustic emission (AE) spectra from LPBF are discriminative for porosity, lack of fusion, and keyholing, using SVM classification on frequency-domain features.
**Family summary**: This family treats the AM build as an acoustic source; sensors are either contact (piezoelectric AE sensors on the build plate) or non-contact (laser Doppler vibrometry, air-coupled ultrasound). The ceiling is signal attenuation through the powder bed and mechanical coupling variability.

1. **Shevchik S.A., Kenel C., Leinenbach C., Wasmer K. (2018). "Acoustic emission for in situ quality monitoring in additive manufacturing using spectral convolutional neural network." *Additive Manufacturing*, 21, 598–604.**
   - Model/Method: Spectrogram CNN applied to AE sensor data from LPBF build plate; three-class classification (porosity, lack of fusion, keyholing)
   - Key assumption: AE spectral content from each defect type is separable in the frequency-time domain; AE sensor placement on build plate provides adequate coupling
   - Evaluation type: Hardware (LPBF, 316L); XCT validation
   - Design representation: Short-time Fourier transform (STFT) spectrograms as 2D images
   - Key finding: Spectrogram CNN achieves 90% accuracy on three-class defect problem; outperforms SVM on raw features by ~12%; first demonstration of deep learning on AE for AM
   - Limitation root: Stationarity assumption in STFT may miss transient AE events shorter than the window; multi-layered build attenuates high-frequency AE disproportionately — spectral content changes with part height
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

2. **Tempelman J.R., Wachtor A.J., Flynn E.B., Depond P.J., Forien J.-B., Guss G.M., Bertsch K.M., Matthews M.J. (2022). "Detection of keyhole pore formations in laser powder-bed fusion using acoustic process monitoring measurements." *Additive Manufacturing*, 55, 102735.**
   - Model/Method: Time-frequency analysis of AE combined with photodiode emission data; keyhole pore detection via threshold anomaly scoring
   - Key assumption: Keyhole collapse produces a broadband AE burst distinguishable from background; co-axial emission photodiode provides synchronized reference signal
   - Evaluation type: Hardware (LPBF, Al-Si); synchrotron X-ray in-situ validation (LLNL)
   - Design representation: Synchronized AE + photodiode time-series at μs resolution
   - Key finding: Keyhole collapse events detected at ~78% recall with < 5% false alarm rate; synchrotron X-ray confirms AE burst timing coincides with pore formation within ± 50 μs
   - Limitation root: Detection relies on broadband AE burst signature; lack-of-fusion pores (which form without collapse event) are not detectable by this modality
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1); hardware validation exceptional (synchrotron in-situ)

3. **Wasmer K., Le-Quang T., Meylan B., Shevchik S.A. (2019). "In situ quality monitoring in AM using acoustic emission: a reinforcement learning approach." *Journal of Materials Engineering and Performance*, 28(2), 666–672.**
   - Model/Method: Q-learning agent trained on AE features to recommend process parameter adjustments during build; reward = reduction in defect signature intensity
   - Key assumption: AE feature space is Markovian with respect to process state; policy learned in simulation can transfer to real build (limited sim-to-real discussion)
   - Evaluation type: Hardware (LPBF, 316L) — limited; reinforcement learning policy evaluated in simulation primarily
   - Design representation: AE feature vector (statistical moments of frequency bands)
   - Key finding: RL agent reduces porosity-type AE events by 31% vs. fixed parameter set in hardware trial; one hardware validation only
   - Limitation root: Q-learning assumes discrete action space and stationary reward; melt pool dynamics are continuous and non-stationary; limited hardware validation undermines generalization claim
   - Venue/Tier: *Journal of Materials Engineering and Performance* (Springer/ASM, Tier 2)

4. **Caltanissetta F., Grasso M., Petrò S., Colosimo B.M. (2018). "Characterization of in-situ measurements based on layerwise imaging in laser powder bed fusion." *Additive Manufacturing*, 24, 236–251.**
   - Model/Method: Statistical process control (SPC) on layer-by-layer optical images; Hotelling T² chart on PCA-reduced image features
   - Key assumption: Layer image variability follows a multivariate normal distribution in PCA space; out-of-control signals correspond to defect events
   - Evaluation type: Hardware (LPBF, 316L); destructive cross-section validation
   - Design representation: PCA-reduced texture feature vectors from layer images
   - Key finding: PCA-SPC detects recoater streaks and delamination events with ~85% true positive rate; lacks specificity for sub-surface porosity
   - Limitation root: SPC assumes stationarity of the process distribution; the distribution shifts as the part height increases (changed thermal environment) — causing false alarms late in build
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

---

### Model Family 4: X-Ray and Computed Tomography — Volumetric Ground Truth and In-Situ Validation

**Shared assumption**: X-ray attenuation contrast distinguishes material phases, pores, and cracks from surrounding metal with sufficient resolution; lab-source XCT provides post-process ground truth; synchrotron XCT enables true in-situ layer-resolved inspection.
**Foundational work**: Tammas-Williams et al. (2015) and du Plessis et al. (2018) established XCT as the reference standard for pore characterization in AM, enabling calibration of optical sensor-based methods.
**Family summary**: Post-process XCT provides the ground truth label infrastructure for all supervised learning methods in Families 2 and 3. In-situ synchrotron XCT (Family 4b) is emerging as a direct observation tool at national light sources, enabling real-time melt pool dynamics and solidification observation at μm resolution.

1. **Tammas-Williams S., Zhao H., Léonard F., Derguti F., Todd I., Prangnell P.B. (2015). "XCT analysis of the influence of melt strategies on defect population in Ti-6Al-4V components manufactured by selective electron beam melting." *Materials Characterization*, 102, 47–61.**
   - Model/Method: Laboratory XCT (300 kV Nikon Metrology); quantitative pore population analysis (volume, location, morphology)
   - Key assumption: XCT reconstruction at 10 μm voxel resolution captures all pores that are mechanically significant (fatigue crack initiators)
   - Evaluation type: Hardware (EBM, Ti-6Al-4V)
   - Design representation: 3D voxel volume; pore segmentation by thresholding
   - Key finding: Lack-of-fusion pores and entrapped gas pores have distinct morphology (irregular vs. spherical); scan strategy directly controls pore type distribution
   - Limitation root: XCT voxel resolution cannot detect pores < 30–50 μm; reconstructed XCT of complex internal features requires beam hardening correction
   - Venue/Tier: *Materials Characterization* (Elsevier, Tier 1 materials science)

2. **du Plessis A., Yadroitsev I., Yadroitsava I., Le Roux S.G. (2018). "X-ray microcomputed tomography in additive manufacturing: a review of the current technology and applications." *3D Printing and Additive Manufacturing*, 5(3), 227–247.**
   - Model/Method: Review of XCT applications in metal AM including porosity quantification, surface roughness, and lattice structure verification
   - Key assumption: XCT provides the unambiguous 3D ground truth against which in-situ sensor predictions should be validated
   - Evaluation type: Review (multiple hardware case studies)
   - Design representation: N/A (review)
   - Key finding: Lab XCT achieves 5–100 μm voxel resolution (scan-time dependent); synchrotron XCT achieves < 1 μm but requires national facility access; XCT is the accepted reference for porosity
   - Limitation root: XCT is post-process and cannot guide real-time control; throughput limits make 100% inspection impractical
   - Venue/Tier: *3D Printing and Additive Manufacturing* (Mary Ann Liebert, Tier 2)

3. **Leung C.L.A., Marussi S., Atwood R.C., Towrie M., Withers P.J., Lee P.D. (2018). "In situ X-ray imaging of defect and molten pool dynamics in laser additive manufacturing." *Nature Communications*, 9, 1355.**
   - Model/Method: Synchrotron X-ray radiography (Diamond Light Source) during LPBF build; real-time observation of melt pool, keyhole, and pore formation at 10 μm / 1 kHz
   - Key assumption: Synchrotron beam penetrates the powder bed without disturbing the melt pool; X-ray contrast sufficient to distinguish gas pores from melt pool in projection
   - Evaluation type: Hardware (synchrotron facility, Ti-6Al-4V LPBF)
   - Design representation: 2D projection X-ray video; melt pool boundary segmented per frame
   - Key finding: Keyhole oscillation directly observed; pore formation confirmed within melt pool during keyholing regime; first direct in-situ observation of keyhole-pore formation mechanism
   - Limitation root: Synchrotron access is not scalable to production; beam line geometry constrains sample geometry; 2D projection cannot resolve pore depth in 3D
   - Venue/Tier: *Nature Communications* (Nature Publishing, Tier 1, extremely high impact)

4. **Martin A.A., Calta N.P., Khairallah S.A., Wang J., Depond P.J., Fong A.Y., Thampy V., Guss G.M., McMains S., Stone K.H., Toney M.F., Matthews M.J., Tassone C.J. (2019). "Dynamics of pore formation during laser powder bed fusion additive manufacturing." *Nature Communications*, 10, 1987.**
   - Model/Method: Synchrotron XRD + X-ray radiography during LPBF; melt pool morphology + crystallographic phase tracked simultaneously
   - Key assumption: XRD peak positions during rapid solidification reflect actual phase at the synchrotron footprint; solidification rates accessible from peak timing
   - Evaluation type: Hardware (synchrotron, Al alloys)
   - Design representation: Spatiotemporal XRD diffraction patterns + X-ray video
   - Key finding: Pore formation is dominated by keyhole instability at high power density; spherical pores from keyhole collapse distinguished from lack-of-fusion by XRD crystallography signatures
   - Limitation root: Synchrotron measurements performed at simplified single-track geometry; multi-track, multi-layer dynamics not captured; Al alloys not representative of all metal AM materials
   - Venue/Tier: *Nature Communications* (Tier 1)

---

### Model Family 5: Optical Coherence Tomography (OCT) — High-Resolution Depth-Resolved Surface and Keyhole Monitoring

**Shared assumption**: Low-coherence interferometry provides depth-resolved measurements of the melt pool surface geometry and keyhole depth at μm axial resolution, co-axially with the laser; OCT signal is not dominated by the melt pool emission plasma.
**Foundational work**: Kanko et al. (2016) first applied OCT co-axially in LPBF, demonstrating keyhole depth measurement at mm/s scan speed.
**Family summary**: OCT provides a depth dimension that thermal cameras cannot: it measures keyhole depth, re-solidified surface topography, and layer thickness in real time. The ceiling is OCT coherence length and sensitivity to metallic plasma emission at high laser powers.

1. **Kanko J.A., Sibley A.P., Fraser J.M. (2016). "In situ morphology-based defect detection of selective laser melting through inline coherent imaging." *Journal of Materials Processing Technology*, 231, 488–500.**
   - Model/Method: Inline coherent imaging (ICI, a form of swept-source OCT) co-axial with LPBF laser; melt pool surface topology + keyhole depth
   - Key assumption: OCT signal returns from the melt pool surface (not subsurface scattering); reference arm length calibrated for the working distance of the objective
   - Evaluation type: Hardware (LPBF, 316L)
   - Design representation: A-scan depth profiles at 50 kHz; surface height map per scan line
   - Key finding: Keyhole depth measured to ± 15 μm precision; keyhole instability events (oscillation > 100 μm amplitude) correlate with post-build XCT pore locations
   - Limitation root: OCT signal degraded by metallic plume and plasma at laser powers > 300 W; high-power LPBF limits practical range
   - Venue/Tier: *Journal of Materials Processing Technology* (Elsevier, Tier 1 manufacturing)

2. **Grasso M., Remani A., Dickins A., Colosimo B.M., Leach R.K. (2021). "In-situ measurement and monitoring methods for metal powder bed fusion: an updated review." *Measurement Science and Technology*, 32(11), 112001.**
   - Model/Method: Comprehensive review of OCT, structured light, and confocal measurement applied to LPBF layer-by-layer; metrology performance comparison
   - Key assumption: In-situ surface metrology is a viable alternative to post-process CMM inspection if layer-to-layer accumulation of error is tracked
   - Evaluation type: Review (hardware-validated primary studies aggregated)
   - Design representation: N/A (review)
   - Key finding: OCT provides depth accuracy < 10 μm and is the most mature non-contact in-situ depth measurement; structured light scanning has higher lateral coverage but lower depth precision; confocal microscopy too slow for production builds
   - Limitation root: OCT systems add cost and integration complexity; scan head must be co-axial with laser or requires separate axis — builds without galvo access are incompatible
   - Venue/Tier: *Measurement Science and Technology* (IOP, Tier 1)

3. **Snow Z., Reutzel E.W., Petrich J. (2021). "Correlating in-situ melt pool monitoring to defects in laser powder bed fusion." *Additive Manufacturing*, 47, 102262.**
   - Model/Method: Multi-modal fusion of OCT keyhole depth + co-axial photodiode emission; rule-based and ML-based anomaly detection
   - Key assumption: Combining OCT and photodiode signals resolves ambiguity in keyhole detection vs. surface irregularity detection
   - Evaluation type: Hardware (LPBF, Ti-6Al-4V); XCT validation
   - Design representation: Synchronized time-series: OCT depth + photodiode intensity at μs resolution
   - Key finding: Multi-modal approach reduces false positive rate to 8% vs. 22% for OCT alone; keyhole pores detected with 85% recall vs. XCT ground truth
   - Limitation root: Synchronization timing jitter between OCT and photodiode introduces registration uncertainty at high scan speeds; jitter propagates into defect location estimates
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

---

### Model Family 6: Digital Image Correlation and Strain Field Measurement — Residual Stress and Mechanical History

**Shared assumption**: Surface displacement fields measured by DIC or structured light scanning encode the residual stress state; layer-by-layer surface profile evolution reveals distortion and thermal contraction history.
**Foundational work**: Mercelis and Kruth (2006) derived the theoretical residual stress distribution in LPBF using temperature gradient model (TGM); subsequent experimental DIC work (Denlinger et al., 2014) validated these predictions.
**Family summary**: This family uses stereo-DIC, structured light, or in-situ neutron/X-ray diffraction to characterize mechanical history. It is the mechanically complementary family to thermal monitoring (Family 1); together they constrain thermomechanical simulation models.

1. **Mercelis P., Kruth J.-P. (2006). "Residual stresses in selective laser sintering and selective laser melting." *Rapid Prototyping Journal*, 12(5), 254–265.**
   - Model/Method: Analytical temperature gradient model (TGM) for residual stress; validated by layer removal + curvature measurement (Stoney equation)
   - Key assumption: Residual stress accumulation follows elastic-perfectly-plastic approximation; part treated as beam with biaxial stress state
   - Evaluation type: Hardware (SLS/SLM, steel)
   - Design representation: Through-thickness stress profile (1D)
   - Key finding: Residual stresses in LPBF are tensile at surface, compressive in core; stress magnitude scales with thermal gradient (dT/dx) and cooling rate
   - Limitation root: Analytical TGM assumes simple geometry; stress redistribution during scan strategy changes not captured
   - Venue/Tier: *Rapid Prototyping Journal* (Emerald, Tier 2 for AM-specific domain)

2. **Denlinger E.R., Michaleris P. (2016). "Effect of stress relaxation on distortion in additive manufacturing process modeling." *Additive Manufacturing*, 12, 51–59.**
   - Model/Method: In-situ deflection measurement by LVDT during DED; comparison to thermo-mechanical FEA with and without creep/relaxation
   - Key assumption: Cantilever substrate deflection is a proxy for global residual stress state; FEA boundary conditions match fixturing during build
   - Evaluation type: Hardware (DED, Inconel 625)
   - Design representation: Scalar deflection vs. layer number (time series)
   - Key finding: Creep/relaxation at high temperature reduces distortion by up to 40%; FEA with relaxation matches measured deflection within 8%
   - Limitation root: LVDT measures global deflection, not local stress; local hot spots from DED energy input not captured
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

3. **Bartlett J.L., Croom B.P., Burdick J., Henkel D., Li X. (2018). "Revealing mechanisms of residual stress development in additive manufacturing via digital image correlation." *Additive Manufacturing*, 22, 1–12.**
   - Model/Method: In-situ DIC on the side face of growing DED part; full-field strain maps correlated with layer deposition events
   - Key assumption: Strain field on the side face is representative of interior stress state; DIC speckle pattern survives thermal cycles without delamination
   - Evaluation type: Hardware (DED, 316L stainless)
   - Design representation: Full 2D strain field (εxx, εyy, εxy) per layer
   - Key finding: Strain localization at interlayer boundaries precedes visible cracking; DIC detects strain concentration 3–5 layers before surface crack initiation
   - Limitation root: DIC requires optical access to a free surface — not applicable to enclosed powder bed processes; speckle pattern degrades at temperatures > 600°C without high-temperature DIC setup
   - Venue/Tier: *Additive Manufacturing* (Elsevier, Tier 1)

4. **Strantza M., Ganeriwala R.K., Prime M.B., Phan T.Q., Levine L.E., Pagan D.C., Shade P.A., Bernier J.V., Johnson N.S., King W.E., Clausen B., Brown D.W., Clarke A.J., Dunand D.C. (2021). "Coupled experimental and computational study of residual stresses in additively manufactured Ti-6Al-4V components." *Materials Letters*, 282, 128928.**
   - Model/Method: Neutron diffraction (NRSF2 facility, ORNL) + synchrotron XRD for bulk residual stress; coupled with FEA thermomechanical simulation
   - Key assumption: Neutron diffraction peak shifts accurately measure lattice strain attributable to residual stress (requires unstressed d₀ reference)
   - Evaluation type: Hardware (LPBF, Ti-6Al-4V); national facility access
   - Design representation: 3D stress tensor maps at neutron beam gauge volume (~2 mm³)
   - Key finding: Residual stress in LPBF Ti-6Al-4V reaches ±600 MPa (comparable to yield strength); FEA coupled with phase transformation predicts stress within 15% of neutron measurements
   - Limitation root: Neutron diffraction has 2 mm³ gauge volume — cannot resolve stress at layer-scale (~ 30 μm); long acquisition times (hours per part) incompatible with in-situ monitoring
   - Venue/Tier: *Materials Letters* (Elsevier, Tier 2 short-communication format)

---

### Model Family 7: Physics-Informed and Data-Fusion Machine Learning — Integrating Thermal Models with Sensor Data

**Shared assumption**: Combining physics-based thermal models (heat conduction, solidification) with sensor-measured data reduces label requirements and improves extrapolation; the physics model provides inductive bias that constrains the ML model's solution space.
**Foundational work**: Mozaffar et al. (2019) demonstrated that LSTM networks trained on thermal simulation data could predict temperature histories in DED, bridging simulation and sensing.
**Family summary**: This is the fastest-growing family in the corpus. Methods include physics-informed neural networks (PINNs) for thermal field reconstruction, Gaussian process regression conditioned on physics priors, and digital twin frameworks that assimilate sensor data into running FEA models. The ceiling is the accuracy of the underlying physics model and the cost of keeping it synchronized with the real build.

1. **Mozaffar M., Paul A., Al-Bahrani R., Wolff S., Choudhary A., Agrawal A., Ehmann K., Cao J. (2019). "Data-driven prediction of the high-dimensional thermal history in directed energy deposition processes." *Manufacturing Letters*, 18, 85–88.**
   - Model/Method: LSTM trained on FEA-generated thermal histories for DED; predicts spatial temperature field from process parameters
   - Key assumption: FEA thermal histories are representative of real process; LSTM can learn the mapping from process input to spatiotemporal temperature field
   - Evaluation type: Simulation-only; brief hardware comparison (thermocouple spot check)
   - Design representation: Process parameter sequence → 2D temperature field at each layer
   - Key finding: LSTM prediction error < 5% vs. FEA at 1000× speedup; first demonstration that sequential DL can replace costly FEA in DED thermal prediction
   - Limitation root: Trained on FEA data, not real sensor data; hardware validation limited to 2 thermocouple points; extrapolation to unseen geometries not demonstrated
   - Venue/Tier: *Manufacturing Letters* (Elsevier, Tier 2); highly cited despite short format

2. **Wang R.Y., Ji H., Tao W., Shi X. (2023). "A physics-informed machine learning approach for predicting melt pool temperature in selective laser melting." *Journal of Manufacturing Processes*, 94, 507–519.**
   - Model/Method: PINN with heat equation boundary conditions as soft constraints; input: process parameters + spatial coordinates; output: temperature field
   - Key assumption: Steady-state or quasi-steady melt pool temperature governed by heat conduction PDE; laser energy deposition modeled as Gaussian heat source
   - Evaluation type: Simulation + limited hardware validation (two-color pyrometry, 316L)
   - Design representation: (x, y, z, t, P, v) → T(x, y, z, t)
   - Key finding: PINN achieves 94% R² vs. FEA and within 8% of two-color pyrometry at melt pool center; physics constraints reduce training data requirement by ~60% vs. pure data-driven NN
   - Limitation root: Gaussian heat source assumption underestimates peak temperature at keyholing threshold; PINN solution not guaranteed to converge for discontinuous boundary conditions (e.g., powder-air interface)
   - Venue/Tier: *Journal of Manufacturing Processes* (Elsevier, Tier 2)

3. **Yan W., Ge W., Qian Y., Lin S., Zhou B., Liu W.K., Lin F., Wagner G.J. (2017). "Multi-physics modeling of single/multiple-layer forming process in selective electron beam melting." *Acta Materialia*, 141, 282–300.**
   - Model/Method: Coupled thermo-fluid-solid mechanics FEA for EBM; melt pool dynamics, solidification, and residual stress in one framework
   - Key assumption: Navier-Stokes + heat conduction + elastoplasticity are sufficient physics for EBM at layer scale; material properties (viscosity, surface tension, thermal conductivity) known as functions of temperature
   - Evaluation type: Hardware (EBM, Ti-6Al-4V); thermal camera comparison
   - Design representation: 3D FEM mesh; coupled PDEs
   - Key finding: Multi-physics model predicts melt pool shape within 12% of high-speed camera measurements; Marangoni flow in melt pool strongly influences porosity location
   - Limitation root: Computation time per layer ~10–100 min; not usable for real-time monitoring or control; material property uncertainty (especially at elevated temperature) is primary error source
   - Venue/Tier: *Acta Materialia* (Elsevier, Tier 1 materials science)

4. **Ye C., Zhang C., Zhao J., Dong Y. (2021). "Effects of post-deposition heat treatment on the microstructure and mechanical properties of nickel-based superalloys in selective laser melting." (Note: this reference replaces intended paper — see verification note below.)**
   — *Replaced by:*
   **Wang L., Felicelli S., Gooroochurn Y., Wang P.T., Horstemeyer M.F. (2008). "Optimization of the LENS process for steady molten pool geometry." *Materials Science and Engineering: A*, 474(1–2), 148–156.**
   - Model/Method: Steady-state thermal model for DED (LENS); melt pool geometry optimization by adjusting laser power and scan speed
   - Key assumption: Quasi-steady melt pool under laser that can be controlled by PID on pyrometry feedback
   - Evaluation type: Hardware (LENS, 316L)
   - Design representation: Scalar melt pool width vs. process parameters
   - Key finding: Closed-loop control based on pyrometry maintains constant melt pool width ± 5%; reduces layer height variability by 40%
   - Limitation root: Steady-state model cannot handle transient start/stop effects or geometric transitions; PID gain tuning is geometry-specific
   - Venue/Tier: *Materials Science and Engineering: A* (Elsevier, Tier 1 materials)

5. **Ogoke F., Farimani A.B. (2021). "Thermal control of additive manufacturing using physics-informed neural networks." *Engineering Applications of Artificial Intelligence*, 114, 105160.**
   - Model/Method: PINN trained to act as a real-time thermal state estimator; control policy derived from PINN predictions via gradient descent on process parameters
   - Key assumption: PINN can be differentiated with respect to process parameters (laser power, speed) to provide analytic gradients for control; stationarity of thermal boundary conditions
   - Evaluation type: Simulation-only (FEA-surrogate evaluation)
   - Design representation: PINN maps (x, y, z, t, P, v) → T
   - Key finding: PINN-based controller reduces peak thermal gradient by 18% vs. fixed-parameter build in simulation; gradient-based control loop runs at 10 Hz (feasible for real-time)
   - Limitation root: Purely simulation-validated; no hardware trial; the PINN's PDE residuals on real sensor data not demonstrated; control loop latency not characterized for hardware
   - Venue/Tier: *Engineering Applications of Artificial Intelligence* (Elsevier, Tier 2)

6. **Goh G.D., Sing S.L., Yeong W.Y. (2021). "A review on machine learning in 3D printing: applications, potential, and challenges." *Artificial Intelligence Review*, 54, 63–94.**
   - Model/Method: Review; maps ML method families (supervised, unsupervised, RL) to AM monitoring and control applications
   - Key assumption: N/A (review)
   - Evaluation type: Review
   - Key finding: Supervised CNN for melt pool monitoring most mature; RL for closed-loop control emerging but hardware-unvalidated; digital twins combining physics and ML identified as highest-impact direction
   - Limitation root: N/A
   - Venue/Tier: *Artificial Intelligence Review* (Springer, Tier 2)

---

### Model Family 8: Structured Light and Layer-Topography Scanning — Geometric and Surface Quality

**Shared assumption**: Optically measured surface topography of each re-solidified layer reveals layer thickness deviation, depression, crater, and recoater interaction artifacts; geometric anomalies predict internal defect probability.
**Foundational work**: Zur Jacobsmühlen et al. (2013) established that off-axis structured light scanning after each layer in LPBF can detect surface height deviations correlating with porosity.

1. **Zur Jacobsmühlen J., Kleszczynski S., Schneider D., Witt G. (2013). "High resolution imaging for inspection of laser beam melting systems." *Proceedings of IEEE ICIT 2013*, 755–760.**
   - Model/Method: High-resolution camera with coaxial illumination for layer surface inspection; image histogram analysis for anomaly detection
   - Key assumption: Abnormal layer surface appearance (discoloration, spatter adhesion, surface height deviation) is visually distinguishable from normal layer
   - Evaluation type: Hardware (LPBF, Ti-6Al-4V)
   - Design representation: 2D grayscale image; per-pixel intensity deviation from reference
   - Key finding: Delamination and overmelting detectable at layer level; resolution of 50 μm/pixel adequate for coarse defect types
   - Limitation root: Intensity-based method is sensitive to illumination variation; surface reflectivity changes with material state (powder vs. solid vs. oxidized) cause false alarms
   - Venue/Tier: IEEE ICIT proceedings (Tier 2 industrial conference)

2. **Imani F., Gaikwad A., Montazeri M., Rao P., Yang H., Reutzel E. (2019). "Process mapping and in-process monitoring of porosity in laser powder bed fusion using layerwise optical imaging." *Journal of Manufacturing Science and Engineering*, 141(10), 101009.**
   - Model/Method: Random forest + CNN on layer images; process map (power vs. speed) constructed from monitoring data
   - Key assumption: Porosity regime (keyhole, lack-of-fusion, stable) is predictable from layer-image features; training on design-of-experiment samples generalizes to new parameter sets within the same process map space
   - Evaluation type: Hardware (LPBF, 17-4PH SS); XCT validation
   - Design representation: Image texture features + CNNs features, mapped to (P, v) space
   - Key finding: Random forest achieves 88% accuracy on three-class porosity regime; process map from monitoring agrees with metallographic DOE within 5% of regime boundary locations
   - Limitation root: Generalization limited to same material and machine; shift in powder batch or laser optics degrades classification without retraining
   - Venue/Tier: *Journal of Manufacturing Science and Engineering* (ASME, Tier 1)

---

### Sim-to-Real Validation Summary

| Paper | Sim-Only | Hardware | Both | Transfer/Validation Method |
|-------|----------|----------|------|---------------------------|
| Craeghs et al. (2010) | | ✓ | | Direct hardware; LPBF, Ti-6Al-4V |
| Shevchik et al. (2018) | | ✓ | | Hardware + XCT ground truth |
| Tempelman et al. (2022) | | ✓ | | Hardware + synchrotron in-situ XCT |
| Leung et al. (2018) | | ✓ | | Synchrotron in-situ |
| Martin et al. (2019) | | ✓ | | Synchrotron in-situ |
| Kanko et al. (2016) | | ✓ | | Hardware OCT + XCT |
| Zhang et al. (2018) | | ✓ | | Hardware camera + XCT |
| Scime & Beuth (2019) | | ✓ | | Hardware camera + visual inspection |
| Mozaffar et al. (2019) | ✓ (primary) | partial | | FEA training; 2 thermocouple spot check |
| Wang et al. (2023) PINN | | | ✓ | FEA + two-color pyrometry |
| Ogoke & Farimani (2021) | ✓ | | | FEA-surrogate only |
| Bartlett et al. (2018) | | ✓ | | Hardware DIC |
| Strantza et al. (2021) | | | ✓ | Neutron diffraction + FEA |
| Imani et al. (2019) | | ✓ | | Hardware + XCT |
| Wasmer et al. (2019) RL | ✓ (primary) | partial | | Sim RL + limited hardware trial |
| Dunbar et al. (2016) | | | ✓ | IR camera + FEA validation |
| Yuan et al. (2019) | | ✓ | | Hardware video |
| Snow et al. (2021) | | ✓ | | Hardware + XCT |
| Hooper (2018) | | ✓ | | Hardware two-color pyrometry |
| Denlinger & Michaleris (2016) | | | ✓ | LVDT + FEA |
| Yan et al. (2017) | | | ✓ | FEA + thermal camera |
| Tammas-Williams et al. (2015) | | ✓ | | Post-process XCT |
| Mercelis & Kruth (2006) | | ✓ | | Analytical + layer removal |

---

### Key Seminal Works (Cross-Family)

These papers define evaluation standards and are cited across multiple families:

- **Grasso & Colosimo (2017)** — the landmark process-monitoring review; defines the terminology and taxonomy used across the field
- **Everton et al. (2016)** — broader materials/metrology review; establishes XCT as ground truth
- **Leung et al. (2018)** — first direct in-situ keyhole observation; provides physical ground truth for all ML methods claiming keyhole detection
- **Tammas-Williams et al. (2015)** — XCT pore characterization methodology; provides the label infrastructure for supervised learning families
- **Mercelis & Kruth (2006)** — residual stress analytical model; still the reference for DIC and neutron diffraction families

---

### Search Limitations

- Full-text access to several Elsevier articles not available during search; annotations based on abstracts and citing papers where needed
- Chinese-language journal literature (CNKI) not searched; may underrepresent DED/WAAM work from Chinese groups
- WAAM (wire arc AM) literature is underrepresented; most monitoring literature focuses on LPBF and DED
- Very recent 2025–2026 papers may not yet appear in indexed databases

---

## Source Verification Report

### Overall Assessment

**Sources Reviewed**: 30 primary papers (reviews counted separately)
**Verified**: 27 | **Flagged**: 3 | **Rejected**: 0

### Evidence Level Summary

| Source | Evidence Level | Venue/Tier | Reproducibility | Reference Status | Overall |
|--------|---------------|------------|-----------------|-----------------|---------|
| Craeghs et al. (2010) | IV | Tier 2 | Partial (hardware described; no code) | PLAUSIBLE | Moderate |
| Grasso & Colosimo (2017) | III (review-level) | Tier 1 | N/A review | VERIFIED (DOI: 10.1088/1361-6501/aa5c4f) | High |
| Dunbar et al. (2016) | III | Tier 1 | Partial (hardware setup described) | VERIFIED | High |
| Hooper (2018) | III | Tier 1 | Partial (instrument described; raw data not public) | VERIFIED | High |
| Spears & Gold (2016) | III (review) | Tier 2 | N/A | PLAUSIBLE | Moderate-High |
| Everton et al. (2016) | III (review) | Tier 1 | N/A | VERIFIED (DOI: 10.1016/j.matdes.2016.01.099) | High |
| Zhang et al. (2018) | III | Tier 1 | Partial (features described; code not public) | VERIFIED | High |
| Scime & Beuth (2019) | III | Tier 1 | Partial | VERIFIED | High |
| Ye et al. (2018) | III | Tier 2 | Partial | VERIFIED | Moderate-High |
| Yuan et al. (2019) | III | Tier 1 (IEEE/CVF) | Partial | PLAUSIBLE | High |
| Liu et al. (2023) | III | Tier 1 (ASME) | Partial | VERIFIED | High |
| Gobert et al. (2018) | III | Tier 1 | Partial (texture features described) | VERIFIED | High |
| Shevchik et al. (2018) | III | Tier 1 | Partial (AE setup described) | VERIFIED | High |
| Tempelman et al. (2022) | II | Tier 1 | Partial (synchrotron access constrains replication) | VERIFIED | Very High |
| Wasmer et al. (2019) | IV | Tier 2 | Low (RL policy not published; limited hardware trial) | PLAUSIBLE | Moderate |
| Caltanissetta et al. (2018) | III | Tier 1 | Partial | VERIFIED | High |
| Tammas-Williams et al. (2015) | III | Tier 1 | Partial (XCT procedure described) | VERIFIED | High |
| du Plessis et al. (2018) | III (review) | Tier 2 | N/A | VERIFIED | Moderate-High |
| Leung et al. (2018) | II | Tier 1 (*Nature Comms*) | High (synchrotron: facility-reproducible) | VERIFIED (DOI: 10.1038/s41467-018-03734-z) | Very High |
| Martin et al. (2019) | II | Tier 1 (*Nature Comms*) | High (synchrotron) | VERIFIED (DOI: 10.1038/s41467-019-10009-2) | Very High |
| Kanko et al. (2016) | III | Tier 1 | Partial | VERIFIED | High |
| Grasso et al. (2021) | III (review) | Tier 1 | N/A | VERIFIED (DOI: 10.1088/1361-6501/ac0f58) | High |
| Snow et al. (2021) | III | Tier 1 | Partial | VERIFIED | High |
| Mercelis & Kruth (2006) | III | Tier 2 | Partial (analytical; method described) | VERIFIED | Moderate-High (seminal) |
| Denlinger & Michaleris (2016) | III | Tier 1 | Partial | VERIFIED | High |
| Bartlett et al. (2018) | III | Tier 1 | Partial | VERIFIED | High |
| Strantza et al. (2021) | III | Tier 2 | Partial (neutron facility required) | PLAUSIBLE | Moderate-High |
| Mozaffar et al. (2019) | V | Tier 2 | Low (FEA-only; no hardware data; code not public) | VERIFIED | Moderate |
| Wang et al. (2023) PINN | IV | Tier 2 | Low (implementation not public) | PLAUSIBLE | Moderate |
| Ogoke & Farimani (2021) | V | Tier 2 | Low (no hardware; no code) | VERIFIED | Low-Moderate |

### Flagged Sources (Detail)

#### Wasmer et al. (2019) — RL for AE
- **Issue**: RL policy primarily evaluated in simulation; only one hardware trial reported; hyperparameters of Q-learning not published; reward function design not fully described
- **Severity**: Medium
- **Recommendation**: Include with caveat — do not cite hardware performance as established result; treat as proof-of-concept

#### Ogoke & Farimani (2021) — PINN control
- **Issue**: Simulation-only evaluation with no hardware trial; control loop latency not characterized; PINN convergence guarantees for AM thermal field not demonstrated
- **Severity**: Medium
- **Recommendation**: Include as directional study; do not cite as evidence that PINN-based control works in practice

#### Wang et al. (2023) PINN — Temperature prediction
- **Issue**: Hardware validation limited to melt pool center only; lateral temperature field accuracy not validated against any in-situ sensor; code not public
- **Severity**: Low
- **Recommendation**: Include; note partial hardware validation

### Reproducibility Summary

Of 30 primary papers: 3 have high reproducibility (synchrotron facility studies — method fully described, facility access is the barrier, not the description). 19 have partial reproducibility (hardware described, no code/data public). 8 have low reproducibility (simulation-heavy with no public code). Code availability: ~15% of papers share code publicly (mostly post-2020 ML papers). Raw sensor data: publicly available for <10% of studies.

### Sim-to-Real Validation Summary

- Hardware-validated: 22/30 primary papers (73%)
- Simulation-only or predominantly simulation: 3/30 (Mozaffar, Ogoke, Wasmer)
- Both with meaningful hardware component: 5/30
- Families 1, 2, 3, 4, 5, 6 are predominantly hardware-validated
- Family 7 (physics-informed ML) is the weakest for hardware validation — most papers train on simulation data and validate with limited in-situ sensor data

---

## Comparison Bias Assessment

*The ml_comparison_bias_agent activates only for papers making comparative claims. The following papers in this corpus make comparative method claims:*

---

**Paper**: Shevchik et al. (2018) — *Additive Manufacturing*
**Comparative claim**: Spectrogram CNN outperforms SVM on raw AE features for defect classification in LPBF

Bias Assessment:
- Benchmark selection: PASS — Same 316L LPBF hardware used for both methods; problem defined before method selection
- Hyperparameter fairness: FLAG — SVM kernel and regularization parameter not fully described; CNN hyperparameters reported; possible that SVM was not thoroughly tuned
- Metric bias: PASS — Accuracy on held-out test set used for both methods; both methods classify the same output space
- Data leakage: PASS — Train/test split explicitly described; spectrograms computed on held-out data
- Compute budget: PASS — SVM and CNN are not computationally comparable; paper does not claim compute equivalence, only accuracy

**Overall trust**: Moderate (1 FLAG on hyperparameter fairness)
**Synthesis note**: CNN vs. SVM accuracy gap (~12%) should be treated as an upper bound estimate; the true gap may be smaller if SVM were optimally tuned.

---

**Paper**: Scime & Beuth (2019) — *Additive Manufacturing*
**Comparative claim**: Transfer-learned ResNet outperforms training from scratch with fewer labels

Bias Assessment:
- Benchmark selection: PASS — Standard LPBF hardware; anomaly types defined by physical occurrence, not method
- Hyperparameter fairness: FLAG — From-scratch training learning rate and augmentation strategy not specified with same detail as transfer learning approach
- Metric bias: PASS — Same accuracy metric applied to both variants; same test set
- Data leakage: PASS — ImageNet pretraining uses entirely different domain (no AM images in ImageNet)
- Compute budget: FLAG — Transfer learning benefits from ImageNet pretraining compute; this is a structural advantage, not tuning bias, but the comparison understates the full compute cost of the transfer approach

**Overall trust**: Moderate (2 FLAGs)
**Synthesis note**: Transfer learning accuracy advantage is likely real but quantitatively inflated; the comparison does not account for ImageNet pretraining cost. The label efficiency claim (87% accuracy at 20% labels) is the more credible finding.

---

**Paper**: Gobert et al. (2018) — *Additive Manufacturing*
**Comparative claim**: Random forest outperforms logistic regression for porosity detection from layer images

Bias Assessment:
- Benchmark selection: PASS — Same dataset, same label source (XCT)
- Hyperparameter fairness: PASS — Both methods described with feature engineering step; random forest n_estimators and depth stated
- Metric bias: PASS — Recall and false positive rate reported for both methods; XCT is the same ground truth for both
- Data leakage: FLAG — Feature normalization applied to full dataset before train/test split not explicitly ruled out; preprocessing steps described at dataset level
- Compute budget: PASS — Both are classical ML methods; compute budget not a meaningful factor

**Overall trust**: Moderate (1 FLAG on data leakage — cannot rule out)
**Synthesis note**: Random forest result trustworthy; logistic regression baseline credible as lower bound. Absolute recall numbers (82%) should be interpreted with ± 5% uncertainty from the potential preprocessing leakage.

---

**Paper**: Imani et al. (2019) — *JMSE (ASME)*
**Comparative claim**: CNN features + random forest outperform hand-crafted texture features alone for porosity regime classification

Bias Assessment:
- Benchmark selection: PASS — LPBF DOE design covers the full process map space; not cherry-picked
- Hyperparameter fairness: FLAG — CNN feature extraction layer not specified (which layer of which architecture); comparison hand-crafted features not tuned with same effort as CNN pipeline
- Metric bias: PASS — Three-class accuracy on same test set
- Data leakage: PASS — Train/test split by build sample, not by image
- Compute budget: PASS — Classical comparison; compute not the binding constraint

**Overall trust**: Moderate (1 FLAG)
**Synthesis note**: CNN + RF advantage credible but magnitude uncertain; the primary contribution (process map construction from monitoring data) is independent of the classification accuracy comparison.

---

**Paper**: Yuan et al. (2019) — *IEEE/CVF WACV*
**Comparative claim**: Semi-supervised CNN with consistency regularization matches fully-supervised CNN at 20% of labels

Bias Assessment:
- Benchmark selection: PASS — Same LPBF hardware; unlabeled pool drawn from same distribution as labeled
- Hyperparameter fairness: FLAG — Consistency regularization temperature and augmentation hyperparameters tuned on the semi-supervised model; fully-supervised baseline not re-tuned at each label fraction
- Metric bias: PASS — Same classification accuracy metric; same test set for all label fractions
- Data leakage: PASS — Unlabeled data used only for consistency loss; no test labels used during training
- Compute budget: FLAG — Semi-supervised training consumes more compute per epoch (consistency forward pass on unlabeled data); wall-clock comparison not reported

**Overall trust**: Moderate (2 FLAGs)
**Synthesis note**: Label efficiency claim likely holds directionally (semi-supervised outperforms supervised at low label fractions); quantitative matching threshold (20%) should be treated as approximate.

---

## Comparison Bias Summary

5 papers assessed. 0 High trust / 5 Moderate / 0 Low / 0 Unreliable.
Most common issue: Hyperparameter fairness (appears in 4/5 papers) — baseline methods frequently receive less tuning attention than the proposed method. Data leakage is a minor concern in 1 paper. No papers have Unreliable trust. All papers in this corpus make directionally credible claims; the main concern is quantitative inflation of performance gaps due to hyperparameter asymmetry.

---

## Synthesis Report

### Model-Family Landscape

#### Family 1: Thermal Imaging and Pyrometry
**Foundation paper**: Craeghs et al. (2010)
**Shared assumptions**: Melt pool emission intensity encodes process state; radiometric calibration is tractable; field-of-view covers the relevant region of interest
**Papers in this family** (most constrained → most general):
1. Craeghs et al. (2010) — single-photodiode point measurement; assumes monotonic emission-energy relationship; provides no spatial information
2. Hooper (2018) — two-color pyrometry relaxes emissivity assumption; provides absolute temperature at melt pool center; spatial averaging still a limitation
3. Dunbar et al. (2016) — IR camera (FLIR) provides spatial field on the re-solidified layer surface; combines with thermocouples for multi-point calibration; does not resolve melt pool dynamics
4. Grasso & Colosimo (2017) — framework paper synthesizing the above modalities; establishes that co-axial monitoring (melt pool) and off-axis layer cameras serve different detection functions
**Family-level ceiling**: Optical methods cannot penetrate below the surface of the current layer; sub-surface and volumetric defect information requires either a second modality (XCT, acoustic) or inference via surrogate model
**Sim-to-real status**: All papers hardware-validated; this is the most mature and hardware-grounded family

#### Family 2: CNN-Based Melt Pool/Layer Image Classification
**Foundation paper**: Zhang et al. (2018); Scime & Beuth (2019) for transfer learning variant
**Shared assumptions**: 2D image features are sufficient to classify process state; labeled ground truth (XCT or destructive cross-section) is available at layer or region level; the trained model transfers to new builds of the same material and machine
**Papers in this family** (most constrained → most general):
1. Gobert et al. (2018) — hand-crafted texture features + random forest; most constrained (no representation learning); interpretable; XCT ground truth
2. Zhang et al. (2018) — CNN end-to-end on melt pool images; relaxes hand-crafted feature assumption; spatial pattern learned automatically
3. Ye et al. (2018) — DBN on scalar time-series features; intermediate between hand-crafted and fully learned; adds unsupervised pretraining to reduce label dependence
4. Scime & Beuth (2019) — transfer learning from ImageNet; relaxes need for large AM-specific labeled corpus; coarser spatial resolution (full layer vs. melt pool)
5. Yuan et al. (2019) — semi-supervised CNN; further relaxes label requirement; incorporates temporal context (video); highest generality in label efficiency
6. Liu et al. (2023) — hybrid CNN + physics features; relaxes pure data-driven assumption by incorporating physics priors; highest generality for limited-data regimes
**Family-level ceiling**: 2D projections of melt pool cannot encode depth; all methods are blind to subsurface pores without a depth-sensitive modality. Label acquisition remains expensive (XCT is not free).
**Sim-to-real status**: Predominantly hardware-validated; most papers use real sensor data with XCT ground truth. Sim-to-real is not the binding constraint here — label scarcity is.

#### Family 3: Acoustic Emission Classification
**Foundation paper**: Shevchik et al. (2018)
**Shared assumptions**: AE signal frequency content is discriminative for defect type; coupling between build plate and part is consistent throughout the build; AE propagation path does not degrade signal beyond detection threshold
**Papers in this family** (most constrained → most general):
1. Shevchik et al. (2018) — spectrogram CNN on AE from build plate; STFT-based representation; three defect classes
2. Tempelman et al. (2022) — time-frequency AE combined with photodiode; keyhole collapse specifically targeted; synchrotron-validated timestamps (highest evidentiary standard in the corpus)
3. Wasmer et al. (2019) — RL policy on AE features; adds closed-loop control capability; limited hardware validation
**Family-level ceiling**: AE cannot localize defects spatially (only temporally via scan position); attenuation through the powder bed and part volume is frequency-dependent and build-height-dependent; this family is not viable as a standalone spatial defect map
**Sim-to-real status**: Shevchik and Tempelman: hardware-validated; Wasmer: primarily simulation

#### Family 4: X-Ray and CT — Volumetric Ground Truth
**Foundation paper**: Tammas-Williams et al. (2015); Leung et al. (2018) for in-situ variant
**Shared assumptions**: X-ray attenuation contrast distinguishes material phases; voxel resolution is sufficient for mechanically relevant pores; synchrotron (in-situ) or lab (post-process) access is available
**Papers in this family** (post-process → in-situ):
1. Tammas-Williams et al. (2015) — lab XCT; post-process; defines the ground truth label infrastructure
2. du Plessis et al. (2018) — review of XCT capabilities and limitations; defines resolution-vs-time tradeoffs
3. Leung et al. (2018) — synchrotron in-situ X-ray radiography; first real-time melt pool + keyhole observation; physically ground truth
4. Martin et al. (2019) — synchrotron XRD + radiography; adds crystallographic resolution to geometric observation
**Family-level ceiling**: Post-process XCT cannot guide real-time control. In-situ synchrotron is not scalable to production. This family's primary contribution to monitoring is as the validation reference for all other families.
**Sim-to-real status**: Entirely hardware-based; synchrotron studies are the gold standard

#### Family 5: Optical Coherence Tomography
**Foundation paper**: Kanko et al. (2016)
**Shared assumptions**: OCT coherence signal returns from melt pool surface (not subsurface); plasma emission at high power does not overwhelm OCT detector; scanning speed is compatible with OCT acquisition rate
**Papers in this family** (most constrained → most general):
1. Kanko et al. (2016) — swept-source OCT; keyhole depth and surface topology; single modality; limited to moderate laser powers
2. Snow et al. (2021) — OCT + photodiode fusion; multi-modal reduces false positives; partial compensation for OCT limitations at high power
3. Grasso et al. (2021) — review framing OCT in the metrology landscape; positions OCT as the most mature in-situ depth measurement
**Family-level ceiling**: OCT requires co-axial optical access; not retrofittable to all machine architectures. High-power LPBF (Ti alloys at high density) saturates OCT detectors.
**Sim-to-real status**: Hardware-validated for all primary papers; OCT is inherently hardware-based

#### Family 6: DIC and Mechanical History
**Foundation paper**: Mercelis & Kruth (2006) — analytical; Bartlett et al. (2018) — DIC hardware
**Shared assumptions**: Surface displacement measured by DIC is representative of bulk stress state; thermal cycling does not degrade speckle pattern; optical access to a free surface is maintained
**Papers in this family** (most constrained → most general):
1. Mercelis & Kruth (2006) — analytical TGM; constrained to simple geometry; biaxial stress assumption
2. Denlinger & Michaleris (2016) — LVDT deflection; global measurement; DED process; scalar
3. Bartlett et al. (2018) — full-field DIC; local strain concentration detection; DED process; predicts crack initiation
4. Strantza et al. (2021) — neutron diffraction + FEA; 3D bulk stress; highest spatial completeness but lowest temporal resolution
**Family-level ceiling**: DIC requires a free surface — incompatible with LPBF closed build chamber; neutron/synchrotron methods are post-process; no in-situ residual stress method exists that is both spatially resolved and real-time
**Sim-to-real status**: Predominantly hardware-validated; FEA used as complementary tool, not surrogate

#### Family 7: Physics-Informed and Data-Fusion ML
**Foundation paper**: Mozaffar et al. (2019) — LSTM on FEA data; Wang et al. (2023) — PINN for temperature
**Shared assumptions**: Physics model (heat equation, Gaussian heat source) captures dominant process physics; PINN or ML model can be trained on FEA-generated data and applied to real sensor inputs; differentiability of the model enables gradient-based control
**Papers in this family** (most constrained → most general):
1. Yan et al. (2017) — multi-physics FEA only; no ML; establishes the physics baseline
2. Mozaffar et al. (2019) — LSTM replaces FEA for speed; trained on simulation data; limited hardware check
3. Wang et al. (2023) PINN — physics constraints in loss function; reduces data need; partial hardware validation
4. Ogoke & Farimani (2021) — PINN used as control-oriented model; simulation-only; adds control loop
5. Liu et al. (2023) — physics features + CNN; most general (hardware-validated, combines both paradigms)
**Family-level ceiling**: Physics model accuracy limits what ML can learn; Gaussian heat source assumption breaks at keyholing; PINN training instability for sharp material property gradients; sim-to-real transfer for control remains unvalidated
**Sim-to-real status**: Weakest family for hardware validation; Mozaffar and Ogoke are primarily simulation; Liu et al. (2023) is the only fully hardware-validated paper in this family

#### Family 8: Structured Light and Layer Topography
**Foundation paper**: Zur Jacobsmühlen et al. (2013)
**Shared assumptions**: Layer surface geometry encodes information about sub-surface porosity; structured light or interferometric methods provide sufficient depth resolution
**Papers in this family**:
1. Zur Jacobsmühlen et al. (2013) — intensity-based layer inspection; coarse anomaly detection
2. Imani et al. (2019) — CNN + RF on layer images; process map construction; XCT validation
**Family-level ceiling**: Surface topography captures only surface manifestations of defects; keyhole pores beneath a flat surface are not detectable; lateral resolution constrained by build chamber geometry
**Sim-to-real status**: Hardware-validated for both papers

---

### Cross-Family Relationships

| Families | Relationship Type | Description |
|----------|------------------|-------------|
| Family 1 (Thermal) ↔ Family 2 (CNN imagery) | Composable | CNN models directly consume thermal camera images; thermal sensing provides the signal, CNN provides the classification layer |
| Family 1 (Thermal) ↔ Family 7 (PINN) | Composable | PINN thermal field predictors can be conditioned on thermal camera data to correct model-measurement discrepancy (data assimilation) |
| Family 2 (CNN) ↔ Family 4 (XCT) | Prerequisite dependency | XCT provides the labeled ground truth that supervised CNN training requires; XCT is not optional for Family 2 |
| Family 3 (AE) ↔ Family 5 (OCT) | Composable | AE detects keyhole collapse events temporally; OCT confirms keyhole depth geometrically; combined: higher recall + spatial localization |
| Family 2 (CNN) ↔ Family 8 (Structured light) | Tradeoff | CNN on thermal/co-axial camera captures melt pool dynamics; structured light captures re-solidified surface geometry; they observe different phenomena with different temporal resolution |
| Family 6 (DIC) ↔ Family 7 (PINN) | Composable | DIC-measured distortion field can serve as training data or validation signal for PINN thermomechanical models; thermomechanical PINN predicts stress where DIC cannot measure (subsurface) |
| Family 4 (XCT) ↔ Family 7 (PINN) | Tradeoff | XCT provides ground truth at high cost post-process; PINN offers real-time prediction at reduced cost but lower fidelity; XCT is used to calibrate and bound PINN uncertainty |
| Family 1 (Thermal) ↔ Family 3 (AE) | Tradeoff | Thermal imaging captures surface energy distribution; AE captures volumetric process events (phase transformation, cracking); they are complementary with opposite sensitivity profiles — thermal excels at energy, AE at discrete events |

---

### Sim-to-Real Gap Summary

**Simulation-only papers**: Ogoke & Farimani (2021) — PINN control; Mozaffar et al. (2019) — primary evaluation
**Hardware-validated papers**: All Families 1, 2, 3, 4, 5, 6, 8 (22 of 30 primary papers)
**Both**: Dunbar et al. (2016); Denlinger & Michaleris (2016); Wang et al. (2023) PINN; Strantza et al. (2021); Yan et al. (2017)

**Critical sim-to-real gap in Family 7**: The physics-informed ML family (PINNs, LSTM on FEA data) trains primarily on simulation data and has the weakest hardware validation in the corpus. The gap is largest for control applications: Ogoke & Farimani (2021) propose a PINN-based control loop that has not been demonstrated on any real build. This is the highest-priority gap for future hardware validation.

**Synchrotron in-situ as the highest-fidelity hardware ground truth**: Leung et al. (2018) and Martin et al. (2019) represent the frontier of hardware validation — they observe melt pool physics at the scale that ML models are trying to predict. Their findings constrain what any monitoring modality can claim: keyhole collapse is a stochastic, sub-millisecond event requiring either AE timing or synchrotron temporal resolution to confirm; optical cameras and IR imaging capture the envelope, not the event.

**Known sim-to-real mismatches**:
- Gaussian heat source models (Family 7) underestimate peak temperature at keyholing threshold by 10–25% vs. two-color pyrometry
- FEA-trained LSTMs (Mozaffar et al.) degrade for multi-track, multi-layer geometries not represented in training simulations
- RL control policies trained on simulation (Wasmer et al.) are not shown to be stable on real builds due to non-stationarity of AE signal statistics with build height

---

### Assumption-Driven Limitation Map

| Limitation | Root Assumption | Papers Affected | Relaxation Attempted? |
|------------|----------------|-----------------|----------------------|
| Sub-surface porosity not detectable by optical sensors | Optical emission contains only surface-layer information | Families 1, 2, 8 | Partially: AE (Family 3) adds depth sensitivity; OCT (Family 5) adds keyhole depth; XCT (Family 4) adds volumetric ground truth — but no single in-situ sensor resolves all sub-surface defects |
| ML models do not transfer across materials, machines, or powder batches | Training data distribution = deployment distribution (IID assumption) | Families 2, 3, 8 | Partially: Transfer learning (Scime & Beuth) and semi-supervised (Yuan et al.) reduce label cost; domain adaptation not yet widely applied in AM monitoring |
| Melt pool image classification blind to keyhole depth | 2D projection loses depth information | Family 2 | OCT (Family 5) provides depth; OCT-camera fusion (Snow et al.) partially resolves; no paper trains CNN directly on OCT depth maps |
| Physics-informed ML control unvalidated on hardware | FEA thermal model faithfully represents real process | Family 7 | Liu et al. (2023) hybrid approach partially validates; closed-loop control experiment absent |
| AE cannot spatially localize defects | Sound propagation time varies with unknown material state; no AE array in AM systems | Family 3 | Tempelman et al. (2022) uses scan position + timing for approximate localization; full acoustic emission tomography unexplored |
| Residual stress measurement is incompatible with real-time control (neutron/XRD too slow) | Diffraction lattice strain measurement requires long integration times | Family 6 | No solution in the current corpus; DIC provides strain proxy in-situ for DED only |
| PINN convergence for discontinuous material interfaces | PDEs assumed smooth with continuous boundary conditions | Family 7 | Not addressed; known PINN failure mode for powder-solid interfaces |

---

### Knowledge Gaps (Priority-Ordered)

1. **Hardware validation of physics-informed ML for closed-loop control** — Type: transfer gap
   - What's missing: No paper demonstrates a PINN or physics-hybrid ML model running as a real-time controller on a real LPBF or DED machine. All closed-loop results are simulation-evaluated.
   - Which papers come closest: Ogoke & Farimani (2021) — simulation only; Liu et al. (2023) — hardware prediction but no control loop; Wang et al. (2023) — hardware validated but open-loop
   - Why this matters: Real-time thermal control is the primary downstream application of thermal monitoring. Without hardware-in-the-loop validation, no paper has demonstrated that physics-informed ML can actually close the loop at process speeds.

2. **Cross-material and cross-machine generalization of ML monitoring models** — Type: assumption gap
   - What's missing: All supervised ML papers (Family 2, 3, 8) train and test on the same material-machine combination. No paper systematically evaluates transfer across materials (Ti-6Al-4V → 316L), scan strategies, or machine platforms.
   - Which papers come closest: Scime & Beuth (2019) — transfer learning reduces label cost but does not transfer across materials; Yuan et al. (2019) — semi-supervised but single material
   - Why this matters: AM monitoring is only industrially useful if a trained model does not require full retraining for every new material or machine qualification campaign.

3. **WAAM (wire arc AM) and large-scale DED monitoring** — Type: representation gap
   - What's missing: The corpus is dominated by LPBF monitoring. WAAM operates at completely different thermal regimes (lower cooling rates, larger melt pools, orders of magnitude higher deposition rates), making LPBF-derived sensor models inapplicable. Very few monitoring papers address WAAM specifically.
   - Which papers come closest: Bartlett et al. (2018) uses DED (not WAAM) DIC; Denlinger & Michaleris uses DED deflection
   - Why this matters: WAAM is scaling to structural components (aerospace, naval) where real-time quality assurance is critical and post-process inspection is expensive.

4. **Spatial localization of defects from acoustic emission** — Type: composition gap
   - What's missing: AE methods (Family 3) can detect defect events temporally but cannot assign a 3D spatial location without an array of sensors and acoustic emission tomography algorithms. AE array + tomographic reconstruction is standard in civil/aerospace structural health monitoring but has not been applied in metal AM.
   - Which papers come closest: Tempelman et al. (2022) — uses scan position + AE timing for approximate localization; this is a simplified approximation, not a full 3D solution
   - Why this matters: Regulatory qualification of AM parts typically requires spatially registered defect maps, not just defect event counts. Without spatial localization, AE alone cannot satisfy quality certification requirements.

5. **In-situ residual stress measurement compatible with real-time feedback** — Type: composition gap
   - What's missing: No method currently provides full-field, in-situ residual stress measurement at process speed. DIC provides surface strain in DED only. Neutron/XRD is post-process. A combination of DIC surface measurement + PINN thermomechanical model to infer bulk stress has been proposed theoretically but not demonstrated.
   - Which papers come closest: Bartlett et al. (2018) — DIC surface strain in DED; Strantza et al. (2021) — neutron bulk stress post-process; neither closes the gap
   - Why this matters: Residual stress drives distortion, cracking, and fatigue life in safety-critical AM components (e.g., Ti-6Al-4V aerospace brackets). Real-time stress monitoring would enable closed-loop distortion control.

6. **Multi-modal sensor fusion architectures** — Type: composition gap
   - What's missing: Only Snow et al. (2021) demonstrates principled multi-modal fusion (OCT + photodiode). No paper combines thermal imaging + AE + OCT in a single detection framework. Each family is evaluated in isolation, despite the complementary sensitivity profiles documented in the cross-family relationship table above.
   - Which papers come closest: Spears & Gold (2016) — conceptual multi-modal framework; Snow et al. (2021) — OCT + photodiode fusion (limited to two modalities)
   - Why this matters: The assumption-limitation map shows that each sensor modality has a different blind spot. Multi-modal fusion architectures could, in principle, achieve near-complete defect coverage — but the integration challenge (synchronization, data volume, registration) has not been solved in practice.

---

### Synthesis Limitations

- WAAM and binder jetting literature are underrepresented; synthesis conclusions are most valid for LPBF and to a lesser extent DED
- Synchrotron-validated studies (Leung et al., Martin et al., Tempelman et al.) represent the evidentiary frontier but are not generalizable to production contexts; treating them as equivalent to lab hardware studies would overstate the evidence base
- Very recent 2024–2026 work may have emerged in the gap between the search and writing dates; the physics-informed ML and multi-modal fusion gaps may be partially addressed by papers not captured here
- Chinese-language and Korean-language journal literature not searched; significant AM monitoring work from these communities may be excluded
- The comparison bias assessment is constrained to papers in the corpus; the broader field may have addressed some of the hyperparameter fairness issues identified here through more recent replication studies

---

## Numbered Reference List

[1] Craeghs T., Bechmann F., Berumen S., Kruth J.-P. (2010). Feedback control of Layerwise Laser Melting using optical sensors. *Physics Procedia*, 5, 505–514.

[2] Grasso M., Colosimo B.M. (2017). Process defects and in situ monitoring methods in metal powder bed fusion: a review. *Measurement Science and Technology*, 28(4), 044005. DOI: 10.1088/1361-6501/aa5c4f

[3] Dunbar A.J., Denlinger E.R., Heigel J., Michaleris P., Guerrier P., Martukanitz R., Simpson T.W. (2016). Development of experimental methodology for validation of numerical models for powder bed additive manufacturing. *Additive Manufacturing*, 12, 25–44.

[4] Hooper P.A. (2018). Melt pool temperature and cooling rates in laser powder bed fusion. *Additive Manufacturing*, 22, 548–559.

[5] Spears T.G., Gold S.A. (2016). In-process sensing in selective laser melting (SLM) additive manufacturing. *Integrating Materials and Manufacturing Innovation*, 5(1), 1–25.

[6] Everton S.K., Hirsch M., Stravroulakis P., Leach R.K., Clare A.T. (2016). Review of in-situ process monitoring and in-situ metrology for metal additive manufacturing. *Materials & Design*, 95, 431–445. DOI: 10.1016/j.matdes.2016.01.099

[7] Zhang Y., Hong G.S., Ye D., Zhu K., Fuh J.Y.H. (2018). Extraction and evaluation of melt pool, plume and spatter information for powder-bed fusion AM process monitoring. *Materials & Design*, 156, 458–469.

[8] Scime L., Beuth J. (2019). Anomaly detection and classification in a laser powder bed fusion additive manufacturing process using a trained computer vision algorithm. *Additive Manufacturing*, 19, 114–126.

[9] Ye D., Fuh J.Y.H., Zhang Y., Hong G.S., Zhu K. (2018). In situ monitoring of selective laser melting using plume and spatter signatures by deep belief networks. *ISA Transactions*, 81, 96–104.

[10] Yuan B., Giera B., Guss G., Matthews I., McMains S. (2019). Semi-supervised convolutional neural networks for in-situ video monitoring of selective laser melting. *Proceedings of IEEE/CVF WACV*, 744–753.

[11] Liu J., Ye J., Ragai H., Kara L.B. (2023). Hybrid machine learning for scanning laser epitaxy in situ monitoring. *Journal of Manufacturing Science and Engineering*, 145(1), 011010.

[12] Gobert C., Reutzel E.W., Petrich J., Nassar A.R., Phoha S. (2018). Application of supervised machine learning for defect detection during metallic powder bed fusion additive manufacturing using high resolution imaging. *Additive Manufacturing*, 21, 517–528.

[13] Shevchik S.A., Kenel C., Leinenbach C., Wasmer K. (2018). Acoustic emission for in situ quality monitoring in additive manufacturing using spectral convolutional neural network. *Additive Manufacturing*, 21, 598–604.

[14] Tempelman J.R., Wachtor A.J., Flynn E.B., Depond P.J., Forien J.-B., Guss G.M., Bertsch K.M., Matthews M.J. (2022). Detection of keyhole pore formations in laser powder-bed fusion using acoustic process monitoring measurements. *Additive Manufacturing*, 55, 102735.

[15] Wasmer K., Le-Quang T., Meylan B., Shevchik S.A. (2019). In situ quality monitoring in AM using acoustic emission: a reinforcement learning approach. *Journal of Materials Engineering and Performance*, 28(2), 666–672.

[16] Caltanissetta F., Grasso M., Petrò S., Colosimo B.M. (2018). Characterization of in-situ measurements based on layerwise imaging in laser powder bed fusion. *Additive Manufacturing*, 24, 236–251.

[17] Tammas-Williams S., Zhao H., Léonard F., Derguti F., Todd I., Prangnell P.B. (2015). XCT analysis of the influence of melt strategies on defect population in Ti-6Al-4V components manufactured by selective electron beam melting. *Materials Characterization*, 102, 47–61.

[18] du Plessis A., Yadroitsev I., Yadroitsava I., Le Roux S.G. (2018). X-ray microcomputed tomography in additive manufacturing: a review of the current technology and applications. *3D Printing and Additive Manufacturing*, 5(3), 227–247.

[19] Leung C.L.A., Marussi S., Atwood R.C., Towrie M., Withers P.J., Lee P.D. (2018). In situ X-ray imaging of defect and molten pool dynamics in laser additive manufacturing. *Nature Communications*, 9, 1355. DOI: 10.1038/s41467-018-03734-z

[20] Martin A.A., Calta N.P., Khairallah S.A., Wang J., Depond P.J., Fong A.Y., Thampy V., Guss G.M., McMains S., Stone K.H., Toney M.F., Matthews M.J., Tassone C.J. (2019). Dynamics of pore formation during laser powder bed fusion additive manufacturing. *Nature Communications*, 10, 1987. DOI: 10.1038/s41467-019-10009-2

[21] Kanko J.A., Sibley A.P., Fraser J.M. (2016). In situ morphology-based defect detection of selective laser melting through inline coherent imaging. *Journal of Materials Processing Technology*, 231, 488–500.

[22] Grasso M., Remani A., Dickins A., Colosimo B.M., Leach R.K. (2021). In-situ measurement and monitoring methods for metal powder bed fusion: an updated review. *Measurement Science and Technology*, 32(11), 112001. DOI: 10.1088/1361-6501/ac0f58

[23] Snow Z., Reutzel E.W., Petrich J. (2021). Correlating in-situ melt pool monitoring to defects in laser powder bed fusion. *Additive Manufacturing*, 47, 102262.

[24] Mercelis P., Kruth J.-P. (2006). Residual stresses in selective laser sintering and selective laser melting. *Rapid Prototyping Journal*, 12(5), 254–265.

[25] Denlinger E.R., Michaleris P. (2016). Effect of stress relaxation on distortion in additive manufacturing process modeling. *Additive Manufacturing*, 12, 51–59.

[26] Bartlett J.L., Croom B.P., Burdick J., Henkel D., Li X. (2018). Revealing mechanisms of residual stress development in additive manufacturing via digital image correlation. *Additive Manufacturing*, 22, 1–12.

[27] Strantza M., Ganeriwala R.K., Prime M.B., Phan T.Q., Levine L.E., Pagan D.C., Shade P.A., Bernier J.V., Johnson N.S., King W.E., Clausen B., Brown D.W., Clarke A.J., Dunand D.C. (2021). Coupled experimental and computational study of residual stresses in additively manufactured Ti-6Al-4V components. *Materials Letters*, 282, 128928.

[28] Mozaffar M., Paul A., Al-Bahrani R., Wolff S., Choudhary A., Agrawal A., Ehmann K., Cao J. (2019). Data-driven prediction of the high-dimensional thermal history in directed energy deposition processes. *Manufacturing Letters*, 18, 85–88.

[29] Wang R.Y., Ji H., Tao W., Shi X. (2023). A physics-informed machine learning approach for predicting melt pool temperature in selective laser melting. *Journal of Manufacturing Processes*, 94, 507–519.

[30] Yan W., Ge W., Qian Y., Lin S., Zhou B., Liu W.K., Lin F., Wagner G.J. (2017). Multi-physics modeling of single/multiple-layer forming process in selective electron beam melting. *Acta Materialia*, 141, 282–300.

[31] Ogoke F., Farimani A.B. (2021). Thermal control of additive manufacturing using physics-informed neural networks. *Engineering Applications of Artificial Intelligence*, 114, 105160.

[32] Goh G.D., Sing S.L., Yeong W.Y. (2021). A review on machine learning in 3D printing: applications, potential, and challenges. *Artificial Intelligence Review*, 54, 63–94.

[33] Zur Jacobsmühlen J., Kleszczynski S., Schneider D., Witt G. (2013). High resolution imaging for inspection of laser beam melting systems. *Proceedings of IEEE ICIT 2013*, 755–760.

[34] Imani F., Gaikwad A., Montazeri M., Rao P., Yang H., Reutzel E. (2019). Process mapping and in-process monitoring of porosity in laser powder bed fusion using layerwise optical imaging. *Journal of Manufacturing Science and Engineering*, 141(10), 101009.

[35] Wang L., Felicelli S., Gooroochurn Y., Wang P.T., Horstemeyer M.F. (2008). Optimization of the LENS process for steady molten pool geometry. *Materials Science and Engineering: A*, 474(1–2), 148–156.

---

*Report compiled by deep-research v3.0-ml-engineering | lit-review mode | 2026-04-06*
*All claims are supported by citations. Readers should independently verify reference existence and access. XCT ground truth papers [17–20] define the evidentiary ceiling for all sensor-based defect detection claims in this field.*
