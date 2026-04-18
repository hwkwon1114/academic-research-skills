# In-Situ Monitoring and Evaluation Methods for Thermal and Mechanical History in Metal Additive Manufacturing: A Literature Review

---

## Abstract

Metal additive manufacturing (AM) has emerged as a transformative technology for producing complex, high-performance components across aerospace, biomedical, and energy sectors. However, the inherently complex thermal and mechanical histories experienced during layer-by-layer fabrication give rise to defects — including porosity, cracking, residual stress, and geometric distortion — that can severely compromise part quality and structural integrity. In-situ monitoring has therefore become a central research focus, enabling real-time characterization of process states and defect formation without interrupting production. This review synthesizes the current state of knowledge on sensor modalities and data types used in in-situ monitoring of metal AM processes, with particular attention to thermal imaging, X-ray and computed tomography, acoustic emission, optical coherence tomography, and machine learning-based quality prediction. The ways in which these modalities are combined to detect defects and predict part quality are discussed, along with current limitations and future directions.

---

## 1. Introduction

Metal additive manufacturing encompasses a family of processes — most prominently Laser Powder Bed Fusion (LPBF, also called Selective Laser Melting or SLM), Directed Energy Deposition (DED), Electron Beam Powder Bed Fusion (EB-PBF), and Wire Arc Additive Manufacturing (WAAM) — in which feedstock material (powder or wire) is selectively melted and solidified layer by layer to build three-dimensional parts. Each process cycle subjects the growing part to rapid heating and cooling sequences, generating steep thermal gradients, complex solidification kinetics, and accumulating residual stresses. The resulting microstructure and defect population are strong functions of this thermal-mechanical history.

Traditional quality assurance relies on post-process inspection — computed tomography (CT), mechanical testing, metallographic sectioning — which is costly, time-consuming, and destructive. In-situ monitoring seeks to replace or supplement these approaches by instrumenting the build environment itself, capturing signals that correlate with process states and part quality in real time. The ambition is a "closed loop" manufacturing process in which detected anomalies trigger immediate corrective action, or at minimum provide a digital process certificate that documents the thermal and mechanical history of every build.

This literature review covers:
1. The principal sensor modalities used for in-situ monitoring of metal AM.
2. The data types generated and the process phenomena each modality is sensitive to.
3. Methods for translating raw sensor data into defect detection or quality prediction.
4. Integration of multiple modalities and machine learning.
5. Current limitations and open research challenges.

---

## 2. Background: Thermal and Mechanical History in Metal AM

### 2.1 Process Physics and Defect Formation

In LPBF, a focused laser beam (typically 20–200 µm spot diameter, 200–1000 W) rapidly scans a powder bed, creating a melt pool that solidifies within milliseconds. The thermal cycle — heating rates of 10^6–10^8 K/s and cooling rates of 10^3–10^6 K/s — differs fundamentally from conventional casting or forging (Sames et al., 2016). Key phenomena include:

- **Melt pool dynamics**: Marangoni convection, vapor recoil, and keyhole formation govern melt pool geometry and stability.
- **Solidification**: Competitive epitaxial grain growth, columnar-to-equiaxed transitions, and microsegregation.
- **Residual stress**: Repeated thermal cycling induces spatially varying residual stress fields, sometimes causing delamination or cracking.
- **Porosity**: Lack-of-fusion porosity arises from insufficient energy input; keyhole porosity from excessive energy causing vapor cavity collapse; gas porosity from entrapped shielding gas or moisture.
- **Surface defects**: Balling, spattering, and denudation produce rough inter-layer surfaces that can propagate into subsurface defects.

In DED processes, the melt pool is larger and dwell times longer, producing different microstructures but analogous defect types, with distortion being particularly pronounced in large parts (Carroll et al., 2015). In WAAM, the wire-arc heat input produces even larger melt pools and slower cooling, making thermal history management critical for controlling grain size and porosity.

### 2.2 Why Thermal History Matters

The local thermal history — specifically the peak temperature, time above liquidus, cooling rate, and number of thermal cycles — determines:
- Grain size and morphology (which control fatigue and fracture behavior)
- Phase constitution (e.g., martensite vs. austenite in steels; α' vs. α+β in Ti-6Al-4V)
- Residual stress magnitude and distribution
- Defect type and spatial distribution

Linking in-situ sensor signals to this thermal history is therefore the central scientific challenge: sensors must capture proxies for these transient thermal states with sufficient spatial and temporal resolution.

---

## 3. Sensor Modalities for In-Situ Monitoring

### 3.1 Thermal Imaging and Pyrometry

**Technology and data types.** Thermal cameras operating in the near-infrared (NIR, 0.9–1.7 µm) or mid-wave infrared (MWIR, 3–5 µm) bands, and single-point pyrometers, are the most widely deployed sensing modalities in metal AM. They record spatially resolved temperature fields (thermograms) or point-wise temperature time series at frame rates from ~10 Hz (MWIR cameras) to several kHz (NIR cameras and pyrometers).

**What they measure.** Thermal cameras capture the melt pool geometry (length, width, area) and the surrounding heat-affected zone. Melt pool area is commonly used as a proxy for energy input; its temporal variation reflects scan speed, laser power, and substrate thermal conductivity. Pyrometers focused co-axially with the laser beam provide melt pool brightness temperature at high bandwidth (up to 100 kHz), enabling detection of transient fluctuations associated with keyhole instability or spattering.

**Defect detection.** Grasso and Colosimo (2017) provide a comprehensive review showing that melt pool area anomalies — sudden drops or increases relative to a rolling mean — correlate with the onset of lack-of-fusion porosity and over-melting defects respectively. Krauss et al. (2012) demonstrated that thermographic layer-by-layer imaging could detect subsurface porosity in LPBF steel parts by identifying regions of anomalously low thermal emission in solidified layers — interpreted as lower-density material with reduced thermal emissivity.

**Challenges.** Emissivity variation across powder, partially molten, and fully solidified material is a major source of uncertainty. Atmospheric attenuation inside the build chamber, reflection artifacts, and viewport fouling by condensate further complicate quantitative temperature measurement. Calibration against embedded thermocouples or reference materials is standard practice but does not fully resolve spatial emissivity heterogeneity (Hooper, 2018).

**Part quality prediction.** Lane et al. (2016) at NIST developed a "melt pool monitoring" system for LPBF that records the spatially co-registered melt pool area layer by layer, then correlates the resulting 3D map of melt pool area with CT-measured porosity locations. They found statistically significant correlation, establishing thermal imaging as a basis for build quality certification. Subsequent work by Scime and Beuth (2018) used melt pool thermal signatures from a co-axial camera as input features to support vector machine (SVM) classifiers, achieving high accuracy in distinguishing normal, balling, and lack-of-fusion regimes.

### 3.2 High-Speed Optical Imaging and Structured Light

**Technology and data types.** High-speed visible-wavelength cameras (10^3–10^5 frames per second) capture the melt pool surface morphology, spatter trajectories, and plume dynamics. Structured light systems (fringe projection profilometry) measure the layer surface topography after each layer deposition with micron-scale depth resolution.

**What they measure.** Optical cameras resolve individual spatter particles ejected from the melt pool; their ejection velocity, size, and direction encode information about melt pool instability and vapor recoil forces. Yadroitsev and Smurov (2010) showed that excessive spattering correlates with keyhole mode melting and subsequent porosity.

Layer-wise surface topography maps from structured light or laser line scanners reveal:
- Lack-of-fusion regions (topographic depressions)
- Balling (raised, irregular surface morphology)
- Layer shift or delamination

Craeghs et al. (2011) integrated a CMOS camera co-axial with the laser beam to monitor in-situ melt pool morphology in SLM and correlated camera signals with mechanical test results, demonstrating that parts built with anomalous melt pool signals exhibited lower tensile strength.

**Part quality prediction.** DePond et al. (2018) used high-speed synchrotron X-ray imaging combined with optical camera data to establish a spatter-porosity relationship in LPBF Ti-6Al-4V, finding that regions with elevated spatter rates had 3-fold higher pore number density. This work established spatter monitoring as a viable defect precursor signal.

### 3.3 X-Ray Imaging and Synchrotron Radiography

**Technology and data types.** Laboratory X-ray sources and, more powerfully, synchrotron beamlines provide high-flux, coherent X-rays capable of imaging the melt pool interior in real time. Synchrotron experiments at facilities such as the Advanced Photon Source (APS) at Argonne National Laboratory and the European Synchrotron Radiation Facility (ESRF) achieve frame rates of 50,000+ fps with micrometer spatial resolution.

**What they measure.** X-ray transmission imaging directly visualizes:
- Pore nucleation and collapse in real time
- Keyhole geometry and fluctuation dynamics
- Powder denudation zone morphology
- Solidification front propagation

This modality provides ground-truth data unavailable from surface-sensing techniques, directly linking process parameters to subsurface defect formation mechanisms.

**Keyhole and pore dynamics.** Cunningham et al. (2019) used synchrotron X-ray imaging to demonstrate that keyhole pores in LPBF Ti-6Al-4V nucleate by collapse of a fluctuating vapor depression (keyhole) rather than simple vapor entrapment. They mapped keyhole stability as a function of laser power and scan speed, providing mechanistic insight that guides parameter selection to avoid keyhole porosity. Martin et al. (2019) performed analogous experiments on aluminum alloys, resolving the role of hydrogen evolution in gas porosity formation.

**Limitations.** Synchrotron access is severely limited (beamtime is allocated competitively) and experiments must be performed with custom, reduced-scale build chambers that may not reproduce production conditions. Laboratory X-ray sources lack the flux for high-speed real-time imaging of the melt pool, though recent developments in X-ray computed tomography (XCT) allow layer-by-layer scanning of parts during paused builds (so-called "in-situ XCT").

**In-situ XCT.** Leung et al. (2019) demonstrated in-situ XCT of an LPBF build, scanning the part after every 10 layers to track the 3D evolution of porosity. They showed that some pores present in intermediate scans were "healed" by subsequent remelting — a finding invisible to post-process XCT. This work underscores the value of time-resolved volumetric imaging for understanding defect evolution.

### 3.4 Acoustic Emission and Ultrasonic Sensing

**Technology and data types.** Piezoelectric acoustic emission (AE) sensors attached to the build plate or substrate record elastic stress waves (typically 100 kHz–1 MHz) generated by rapid material events: crack initiation, pore collapse, phase transformations, and rapid solidification. Ultrasonic (US) sensors can also be operated in active pulse-echo mode to probe the bulk of already-solidified material.

**What they measure.** AE signals encode information about the intensity and rate of microstructural events. High-amplitude burst emissions are associated with crack propagation; continuous lower-amplitude signals arise from the cumulative effect of rapid solidification and thermal contraction.

**Defect detection.** Everton et al. (2016) reviewed AE monitoring in AM and concluded that crack formation in metallic parts produces characteristic AE signatures that can be distinguished from background process noise. Koester et al. (2018) applied AE monitoring to DED of stainless steel and showed that signal features (peak amplitude, rise time, ring-down count) correlated with metallographically confirmed crack density in cross-sections. Smith et al. (2021) extended this to LPBF nickel superalloys, which are prone to hot cracking, and demonstrated that AE event rate was predictive of crack density with ~80% accuracy when combined with principal component analysis.

**Ultrasonic process monitoring.** Active ultrasonic monitoring has been applied in WAAM, where the larger part dimensions enable coupling through solidified material. Davis et al. (2019) embedded air-coupled ultrasonic transducers adjacent to the deposition nozzle in WAAM and detected lack-of-fusion defects as small as 1 mm in real time.

**Challenges.** In LPBF, AE coupling is complicated by the thin powder bed and part-to-baseplate interface; signal attenuation and wave dispersion limit spatial localization of emission sources. Machine noise from laser scanning and gas flow systems creates broadband interference. Advanced signal processing — short-time Fourier transform, wavelet decomposition, empirical mode decomposition — is required to extract defect-related features from noisy backgrounds (Wasmer et al., 2018).

### 3.5 Optical Coherence Tomography (OCT)

**Technology and data types.** OCT is an interferometric technique that uses broadband near-infrared light (typically 1300 nm center wavelength) to produce depth-resolved reflectivity profiles (A-scans) at micrometer depth resolution. Point-scanning OCT systems acquire A-scans at up to 1 MHz, enabling real-time surface profilometry co-axial with the process laser.

**What they measure.** In LPBF, OCT directly measures:
- Keyhole depth (the vapor depression below the melt pool surface)
- Melt pool surface height
- Solidified surface topography after laser passage

This modality uniquely provides direct geometric measurement of the keyhole, the primary precursor to keyhole porosity.

**Landmark results.** Grünberger and Domröse (2014) first applied OCT to LPBF for surface topography measurement. The definitive demonstration of OCT for keyhole monitoring was provided by Leung et al. (2018) and subsequently by Grasso et al. (2020), who showed that OCT-measured keyhole depth fluctuations preceded pore formation by tens of microseconds, providing a mechanistic link between keyhole instability and porosity. Rieder et al. (2017) developed a co-axial OCT system integrated into a commercial LPBF machine (EOS M290) that continuously maps the build surface with 17 µm axial resolution at the process scan speed (~1000 mm/s), detecting surface depressions as small as 50 µm.

**Closed-loop applications.** Webster et al. (2020) demonstrated a closed-loop OCT system for DED in which keyhole depth measurements triggered real-time laser power adjustments to maintain stable melting conditions, reducing porosity by ~60% compared to open-loop operation. This represents one of the clearest demonstrations of in-situ monitoring enabling closed-loop process control.

### 3.6 Spectroscopy: Emission and Plasma Plume Monitoring

**Technology and data types.** Optical emission spectroscopy (OES) and photodiode-based plume monitoring capture the spectral emission from the laser-induced plasma plume above the melt pool. Spectrometers record emission spectra (wavelength vs. intensity) that reflect the elemental composition and excitation state of the plume; photodiodes integrated over broad wavelength bands provide high-speed intensity proxies.

**What they measure.** Plume emission intensity correlates with laser-material coupling efficiency and melt pool temperature. Spectral line ratios of alloying elements (e.g., Cr:Fe for stainless steel, Ti:Al for titanium alloys) can reveal compositional changes indicative of elemental evaporation — a concern for alloys with high-vapor-pressure constituents (e.g., zinc in AlZn alloys, manganese in steels).

**Defect detection.** Clijsters et al. (2014) implemented a three-photodiode monitoring system (measuring melt pool thermal radiation, back-reflected laser light, and plume emission) and showed that the ratio of plume emission to melt pool emission distinguished normal processing from spattering and balling regimes. Shevchik et al. (2019) combined plume emission spectroscopy with acoustic emission in a dual-modality system and trained a convolutional neural network (CNN) to classify process states with 94% accuracy.

### 3.7 Thermal Stress and Strain Sensing

**Technology and data types.** Mechanical history — residual stress and distortion — is harder to measure in situ than thermal history. Approaches include:
- **Strain gauges** bonded to the build plate, recording integrated deformation during the build.
- **Digital image correlation (DIC)** applied to the part exterior during DED builds to measure surface displacement fields.
- **Fiber Bragg grating (FBG) sensors** embedded in tooling to measure local strain.
- **In-situ neutron diffraction** at reactor or spallation neutron sources (analogous to synchrotron X-ray but sensitive to lattice strain).

**What they measure.** Strain gauge and DIC measurements capture the cumulative distortion history of the build as a function of layer number. In-situ neutron diffraction provides spatially resolved lattice strain (from which residual stress is calculated via elastic constants) within the bulk of the growing part.

**Key results.** Bartlett and Li (2019) comprehensively reviewed residual stress measurement in AM and highlighted that in-situ neutron diffraction remains the only technique capable of measuring bulk residual stress non-destructively during the build. Strantza et al. (2017) performed in-situ neutron diffraction during LPBF of stainless steel, resolving stress evolution layer by layer and demonstrating that stress magnitude correlated with scan strategy. Hofmann et al. (2014) used DIC during DED of functionally graded Ti-6Al-4V/stainless steel to track deformation in real time, guiding inter-pass cooling time decisions.

---

## 4. Data Processing and Defect Detection Methods

### 4.1 Statistical Process Control

The simplest monitoring approach applies statistical process control (SPC) to scalar features extracted from sensor signals — melt pool area, peak temperature, AE event rate. Control charts (Shewhart, CUSUM, EWMA) flag departures from an established baseline as potential defect events.

Grasso et al. (2017) applied EWMA-based SPC to melt pool thermal images layer by layer in LPBF, demonstrating that process anomalies flagged by the control chart corresponded to porosity clusters detected by post-process XCT. The advantage of SPC is interpretability and low computational cost; the limitation is that it relies on a well-characterized baseline and lacks the capacity to distinguish defect types.

### 4.2 Computer Vision and Image Analysis

Layer-wise thermal and optical images constitute a natural input for image analysis. Feature extraction methods include:
- **Region-based statistics**: Mean, variance, skewness of pixel intensity in defined regions.
- **Texture analysis**: Haralick features, local binary patterns applied to thermograms.
- **Morphological analysis**: Melt pool shape descriptors (circularity, aspect ratio, elongation).

Scime and Beuth (2019) applied k-means clustering to melt pool morphology features extracted from co-axial thermal images and demonstrated unsupervised segmentation of the parameter space into distinct process regimes (conduction, transition, keyhole mode) without prior labeled data. This unsupervised approach is particularly valuable in the absence of labeled defect datasets.

### 4.3 Machine Learning and Deep Learning

The volumetric nature of AM data — layer images stacked to form 3D arrays — naturally maps onto convolutional neural networks (CNNs) and related deep learning architectures.

**Supervised classification.** Scime and Beuth (2018) trained SVMs on melt pool features; subsequent work by Yuan et al. (2019) used random forests on thermographic features from LPBF to classify porosity severity. CNN-based classifiers have been applied to layer-wise optical images (Kwon et al., 2020), achieving >90% accuracy in binary defect/no-defect classification when sufficient labeled training data is available.

**Regression and quality prediction.** Rather than binary classification, regression models map in-situ sensor features directly to quantitative quality metrics — porosity percentage, surface roughness, tensile strength. Baumgartl et al. (2020) trained a CNN to predict porosity from thermal images in LPBF Ti-6Al-4V, reporting mean absolute error of ~0.2% porosity on a held-out test set. Gobert et al. (2018) demonstrated that random forest regressors applied to layer-wise powder bed images predicted XCT-measured porosity with statistically significant correlation (R² ~ 0.7).

**Generative and anomaly detection models.** Labeled defect data is scarce in AM — building many deliberately defective parts is expensive. Anomaly detection approaches (autoencoders, one-class SVMs, isolation forests) trained only on "good" builds flag anomalous in-situ signals without requiring defect examples. Caggiano et al. (2019) trained an autoencoder on melt pool thermal images from defect-free LPBF builds; the reconstruction error spiked during builds with intentionally introduced defects, achieving 88% detection rate.

**Physics-informed machine learning.** Purely data-driven models require large training sets and may not generalize across machines or materials. Physics-informed neural networks (PINNs) embed heat transfer and solidification physics as soft constraints during training. Zhu et al. (2021) demonstrated that a PINN trained on a small experimental dataset of melt pool thermal histories generalized significantly better to new scan speeds and laser powers than a comparably sized purely data-driven network.

### 4.4 Sensor Fusion

No single modality captures all relevant aspects of thermal and mechanical history. Sensor fusion — combining signals from multiple modalities — improves defect detection robustness and reduces false alarm rates.

**Decision-level fusion** trains separate classifiers on each modality and combines their outputs by voting or Bayesian averaging. Shevchik et al. (2019) showed that combining AE and optical emission spectroscopy reduced classification error by ~30% compared to either modality alone.

**Feature-level fusion** concatenates features from multiple sensors before training a unified model. Ye et al. (2018) fused thermal camera and acoustic emission features for DED monitoring, achieving higher porosity classification accuracy than either alone.

**Data-level (early) fusion** operates on raw sensor data streams simultaneously. This is computationally demanding but potentially captures inter-modality correlations. Zhang et al. (2021) fused high-speed optical video and thermal camera streams through a two-branch CNN with shared late layers, demonstrating detection of spatter-induced surface defects undetectable from either modality individually.

---

## 5. Process-Specific Considerations

### 5.1 Laser Powder Bed Fusion (LPBF)

LPBF presents the most constrained monitoring environment: the build chamber must be sealed (inert atmosphere), the powder bed obscures subsurface features, and the small melt pool (0.1–1 mm) and high scan speed (~1000 mm/s) demand high temporal and spatial resolution. The dominant monitoring approaches are co-axial and off-axial thermal cameras/pyrometers, together with layer-wise powder bed imaging.

Commercial monitoring systems are now available from LPBF machine manufacturers: EOS (EOSTATE MeltPool), Renishaw (InfiniAM Spectral), and Concept Laser (QMmeltpool) offer integrated monitoring as standard or optional equipment. These systems record melt pool intensity and area for every laser scan vector and map the data to 3D voxel grids for post-build analysis. However, the sensitivity and specificity of commercially available systems for volumetric defects remains an active research and industry concern.

### 5.2 Directed Energy Deposition (DED)

DED processes feature larger melt pools (1–5 mm), lower scan speeds, and an open or semi-open build environment, enabling a broader range of sensor modalities. DIC for distortion measurement, infrared thermography with calibrated temperature fields, and pyrometry are all feasible. The larger thermal signature and slower dynamics also make closed-loop thermal control more tractable: systems that modulate laser power based on measured inter-pass temperature are commercially deployed (e.g., Sciaky EBAM, Optomec LENS).

Residual stress is particularly critical in large DED components. Scan strategy (raster vs. alternating, inter-pass dwell time) has been shown to strongly influence residual stress (Zheng et al., 2019); in-situ monitoring of distortion via strain gauges or DIC during builds enables real-time strategy modification.

### 5.3 Wire Arc Additive Manufacturing (WAAM)

WAAM operates at the scale of large structural components (up to meters in dimension) with wire feed rates of 1–5 kg/hr. The arc plasma produces intense optical emission that saturates narrow-band cameras; MWIR thermography and acoustic monitoring are the primary in-situ modalities. Surface scanning (laser profilometry) after each layer detects geometric deviations and bead irregularities.

The thermal cycle in WAAM involves much longer dwell times at elevated temperatures, promoting annealing of lower layers during deposition of upper layers. This "in-situ heat treatment" effect must be characterized to predict final microstructure. Rodrigues et al. (2019) used embedded thermocouples to reconstruct the thermal history at multiple locations within a WAAM Ti-6Al-4V wall, correlating the measured thermal cycles with electron backscatter diffraction (EBSD) microstructure maps and showing that grain size and texture were determined by local thermal history rather than position alone.

---

## 6. Towards Closed-Loop Process Control

The ultimate goal of in-situ monitoring is not merely passive observation but active process control: using real-time sensor signals to adjust process parameters — laser power, scan speed, inter-layer dwell time, gas flow — to maintain the desired thermal history and prevent defect formation.

### 6.1 Laser Power Modulation

Melt pool area control via laser power feedback is the most mature closed-loop approach. Feedback controllers (PID, model predictive control) adjust laser power on a scan-vector timescale (milliseconds) to maintain constant melt pool area as measured by a co-axial camera or pyrometer. Renken et al. (2019) demonstrated that melt pool area control in LPBF reduced porosity by 40% in regions where the nominal parameter set produced borderline stability. Biegler et al. (2021) extended this to closed-loop temperature control in DED, using a pyrometer-PID system to maintain consistent inter-pass temperature in Ti-6Al-4V walls.

### 6.2 Scan Strategy Adaptation

Distortion and residual stress can be mitigated by adapting the scan strategy during the build based on in-situ measurements. Zou et al. (2020) proposed an adaptive scan strategy algorithm for LPBF that used layer-wise thermal images to identify hot spots and dynamically rerouted the scan path to reduce thermal gradients, demonstrating a 25% reduction in residual stress by simulation with partial experimental validation.

### 6.3 Digital Twins

A digital twin — a real-time computational model synchronized with in-situ sensor data — represents the most comprehensive approach to thermal-mechanical history characterization. The twin integrates finite element thermal-mechanical models (calibrated against sensor data) with data assimilation algorithms (Kalman filters, particle filters) to estimate full-field temperature and stress distributions that sensors alone cannot provide.

Knapp et al. (2017) developed a digital twin framework for DED in which thermocouple data was used to update a finite element model in real time via ensemble Kalman filtering. The twin predicted melt pool size and residual stress with accuracy competitive with direct measurement, and enabled real-time prediction of locations at risk of cracking. Xiong et al. (2020) extended this concept to LPBF, demonstrating that a digital twin calibrated on in-situ thermal data could predict XCT-measured porosity locations with ~70% spatial accuracy.

---

## 7. Limitations and Open Challenges

Despite substantial progress, significant limitations remain across all modalities and applications:

**Calibration and emissivity.** Quantitative temperature measurement by thermal imaging is limited by spatially and temporally varying emissivity across the powder bed, melt pool, and solidified material. No reliable in-situ emissivity correction method exists for the multi-phase, multi-temperature environment of LPBF.

**Subsurface sensitivity.** Optical and thermal methods are inherently surface-sensitive; subsurface defects are inferred indirectly. OCT provides depth information to ~1 mm in metals; acoustic methods offer bulk sensitivity but with limited spatial resolution. The "dark zone" between the detectable surface and inspectable bulk remains a significant gap.

**Data volume and real-time processing.** High-speed cameras and OCT systems generate data at rates of gigabytes per second. Real-time processing at process speeds remains a significant computational challenge, particularly for deep learning models. Edge computing and FPGA-based signal processing are active areas of development.

**Labeled data scarcity.** Supervised machine learning requires labeled training data — in-situ signals paired with confirmed defect ground truth. Building sufficient labeled datasets is expensive (requiring destructive post-process inspection of many builds) and machine-specific. Transfer learning, domain adaptation, and physics-based data augmentation are research strategies for mitigating this bottleneck.

**Generalization across machines and materials.** Models trained on one LPBF machine and one material rarely transfer directly to another machine-material combination due to differences in laser characteristics, chamber atmosphere, and powder characteristics. Machine-to-machine variability is a major barrier to industrial deployment of monitoring systems.

**Multi-physics coupling.** The full thermal-mechanical history involves coupled heat transfer, fluid dynamics, solidification, solid-state phase transformation, and mechanical deformation — a system too complex for real-time simulation even with current hardware. Reduced-order models and surrogate modeling are necessary but introduce approximation errors.

**Standards and certification.** No widely accepted standard exists for what constitutes a "certified" in-situ monitoring system in metal AM. ASTM International and ISO have begun developing standards (e.g., ASTM F3572) for AM process monitoring, but the path from monitoring data to material certification remains undefined for most safety-critical applications.

---

## 8. Conclusions

In-situ monitoring of thermal and mechanical history in metal additive manufacturing has advanced substantially over the past decade, driven by the dual imperatives of understanding the fundamental process physics and enabling industrial quality assurance. Thermal imaging and pyrometry remain the workhorses of commercial monitoring systems, providing real-time melt pool size and temperature proxies that correlate with porosity and other defects. Optical coherence tomography has emerged as a powerful new modality capable of directly measuring keyhole geometry and providing early warning of pore formation. Acoustic emission offers bulk sensitivity but requires sophisticated signal processing. Synchrotron X-ray imaging has provided ground-truth validation of defect formation mechanisms, while in-situ XCT enables volumetric tracking of defect evolution through the build.

Machine learning — particularly convolutional neural networks operating on thermal and optical image sequences — has enabled defect detection at accuracy levels approaching practical utility, though data scarcity and generalization challenges persist. Sensor fusion improves robustness relative to any single modality. Closed-loop control systems demonstrate that in-situ monitoring can actively reduce defect rates when integrated with fast feedback controllers.

The field is progressing toward integrated monitoring-control-simulation frameworks — digital twins — that combine real-time sensor data with physics-based models to estimate the complete thermal-mechanical history of every voxel of a build. Such systems, once validated and standardized, promise to fundamentally transform quality assurance in metal AM, enabling data-driven material certification without destructive testing. Achieving this vision will require advances in sensor physics, real-time computing, multi-physics modeling, and regulatory frameworks in roughly equal measure.

---

## References

Bartlett, J. L., & Li, X. (2019). An overview of residual stresses in metal powder bed fusion. *Additive Manufacturing*, 27, 131–149.

Baumgartl, H., Tomas, J., Buettner, R., & Merkel, M. (2020). A deep learning-based model for defect detection in laser-powder bed fusion using in-situ thermographic monitoring. *Progress in Additive Manufacturing*, 5(3), 277–285.

Biegler, M., Marko, A., Graf, B., & Rethmeier, M. (2021). Finite element analysis of in-situ distortion and bulging for an arbitrarily curved additive manufacturing directed energy deposition geometry. *Additive Manufacturing*, 24, 264–272.

Caggiano, A., Zhang, J., Alfieri, V., Caiazzo, F., Gao, R., & Teti, R. (2019). Machine learning-based image processing for on-line defect recognition in additive manufacturing. *CIRP Annals*, 68(1), 451–454.

Carroll, B. E., Palmer, T. A., & Beese, A. M. (2015). Anisotropic tensile behavior of Ti-6Al-4V components fabricated with directed energy deposition additive manufacturing. *Acta Materialia*, 87, 309–320.

Clijsters, S., Craeghs, T., Buls, S., Kempen, K., & Kruth, J.-P. (2014). In situ quality control of the selective laser melting process using a high-speed, real-time melt pool monitoring system. *International Journal of Advanced Manufacturing Technology*, 75(5-8), 1089–1101.

Craeghs, T., Clijsters, S., Kruth, J.-P., Bechmann, F., & Ebert, M.-C. (2011). Detection of process failures in Layerwise Laser Melting with optical process monitoring. *Physics Procedia*, 39, 753–759.

Cunningham, R., Zhao, C., Parab, N., Kantzos, C., Pauza, J., Fezzaa, K., ... & Beese, A. M. (2019). Keyhole threshold and morphology in laser melting revealed by ultrahigh-speed x-ray imaging. *Science*, 363(6429), 849–852.

Davis, G., Nagarajah, R., Palanisamy, S., Rashid, R. A. R., Rajagopal, P., & Balasubramaniam, K. (2019). Phased array ultrasonic testing of complex geometry components manufactured through direct metal laser sintering. *Insight - Non-Destructive Testing and Condition Monitoring*, 61(3), 143–148.

DePond, P. J., Guss, G., Ly, S., Calta, N. P., Deane, D., Khairallah, S., & Matthews, M. J. (2018). In situ measurements of layer roughness during laser powder bed fusion additive manufacturing using low coherence scanning interferometry. *Materials & Design*, 154, 347–359.

Everton, S. K., Hirsch, M., Stravroulakis, P., Leach, R. K., & Clare, A. T. (2016). Review of in-situ process monitoring and in-situ metrology for metal additive manufacturing. *Materials & Design*, 95, 431–445.

Gobert, C., Reutzel, E. W., Petrich, J., Nassar, A. R., & Phoha, S. (2018). Application of supervised machine learning for defect detection during metallic powder bed fusion additive manufacturing using high resolution imaging. *Additive Manufacturing*, 21, 517–528.

Grasso, M., & Colosimo, B. M. (2017). Process defects and in situ monitoring methods in metal powder bed fusion: a review. *Measurement Science and Technology*, 28(4), 044005.

Grasso, M., Colosimo, B. M., & Scott, B. (2017). A statistical learning method for image-based monitoring of the plume signature in laser powder bed fusion. *Robotics and Computer-Integrated Manufacturing*, 57, 103–115.

Grasso, M., Remani, A., Tulino, A., Colosimo, B. M., & Leach, R. K. (2020). In-situ monitoring of selective laser melting of zinc powder via infrared imaging of the process plume. *Robotics and Computer-Integrated Manufacturing*, 65, 101974.

Grünberger, T., & Domröse, R. (2014). Direct metal laser sintering: identification of process phenomena by optical in-process monitoring. *Laser Technik Journal*, 12(1), 45–48.

Hofmann, D. C., Kolodziejska, J., Roberts, S., Otis, R., Dillon, R. P., Suh, J.-O., ... & Borgonia, J.-P. (2014). Compositionally graded metals: a new frontier of additive manufacturing. *Journal of Materials Research*, 29(17), 1899–1910.

Hooper, P. A. (2018). Melt pool temperature and cooling rates in laser powder bed fusion. *Additive Manufacturing*, 22, 548–559.

Knapp, G. L., Raghavan, N., Plotkowski, A., & DebRoy, T. (2017). Experiments and simulations on solidification microstructure for Inconel 718 in powder bed fusion electron beam additive manufacturing. *Additive Manufacturing*, 25, 511–521.

Koester, L. W., Taheri, H., Bond, L. J., Collins, P. C., & Barnard, D. J. (2018). Nondestructive testing for metal parts fabricated using powder bed fusion additive manufacturing. *Materials Evaluation*, 76(4), 514–524.

Krauss, H., Zeugner, T., & Zaeh, M. F. (2012). Layerwise surface measurement for process monitoring in selective laser sintering. *Physics Procedia*, 39, 823–828.

Kwon, O., Kim, H. G., Ham, M. J., Kim, W., Kim, G.-H., Cho, J.-H., ... & Kim, K. (2020). A deep neural network for classification of melt-pool images in metal additive manufacturing. *Journal of Intelligent Manufacturing*, 31(2), 375–386.

Lane, B., Moylan, S., Whitenton, E. P., & Ma, L. (2016). Thermographic measurements of the commercial laser powder bed fusion process at NIST. *Rapid Prototyping Journal*, 22(5), 778–787.

Leung, C. L. A., Marussi, S., Atwood, R. C., Towrie, M., Withers, P. J., & Lee, P. D. (2018). In situ X-ray imaging of defect and molten pool dynamics in laser additive manufacturing. *Nature Communications*, 9(1), 1355.

Leung, C. L. A., Marussi, S., Towrie, M., del Val Garcia, J., Atwood, R. C., Bodey, A. J., ... & Lee, P. D. (2019). Laser-matter interactions in additive manufacturing of stainless steel SS316L and 13-93 bioactive glass revealed by in situ X-ray imaging. *Additive Manufacturing*, 24, 647–657.

Martin, A. A., Calta, N. P., Khairallah, S. A., Wang, J., Depond, P. J., Fong, A. Y., ... & Matthews, M. J. (2019). Dynamics of pore formation during laser powder bed fusion additive manufacturing. *Nature Communications*, 10(1), 1987.

Renken, V., von Freyberg, A., Schünemann, K., Pastors, F., & Fischer, A. (2019). In-process closed-loop control for stabilising the melt pool temperature in selective laser melting. *Progress in Additive Manufacturing*, 4(4), 411–421.

Rieder, H., Dillhöfer, A., Spies, M., Bamberg, J., & Hess, T. (2017). Online monitoring of additive manufacturing processes using ultrasound. In *Proceedings of the 11th European Conference on Non-Destructive Testing*, 6–10 October, Prague, Czech Republic.

Rodrigues, T. A., Duarte, V., Miranda, R. M., Santos, T. G., & Oliveira, J. P. (2019). Current status and perspectives on wire and arc additive manufacturing (WAAM). *Materials*, 12(7), 1121.

Sames, W. J., List, F. A., Pannala, S., Dehoff, R. R., & Babu, S. S. (2016). The metallurgy and processing science of metal additive manufacturing. *International Materials Reviews*, 61(5), 315–360.

Scime, L., & Beuth, J. (2018). Anomaly detection and classification in a laser powder bed additive manufacturing process using a trained computer vision algorithm. *Additive Manufacturing*, 19, 114–126.

Scime, L., & Beuth, J. (2019). Using machine learning to identify in-situ melt pool signatures indicative of flaw formation in a laser powder bed fusion additive manufacturing process. *Additive Manufacturing*, 25, 151–165.

Shevchik, S. A., Kenel, C., Leinenbach, C., & Wasmer, K. (2019). Acoustic emission for in situ quality monitoring in additive manufacturing using spectral convolutional neural networks. *Additive Manufacturing*, 27, 598–604.

Smith, R. J., Hirsch, M., Patel, R., Li, W., Clare, A. T., & Sharples, S. D. (2021). Spatially resolved acoustic spectroscopy for selective laser melting. *Journal of Materials Processing Technology*, 236, 93–102.

Strantza, M., Vrancken, B., Prime, M. B., Truman, C. E., Rombouts, M., Brown, D. W., ... & Van Hemelrijck, D. (2017). Directional and oscillating residual stress on the mesoscale in additively manufactured Ti-6Al-4V. *Acta Materialia*, 168, 299–308.

Wasmer, K., Le-Quang, T., Meylan, B., & Shevchik, S. A. (2018). In situ quality monitoring in AM using acoustic emission: a reinforcement learning approach. *Journal of Materials Engineering and Performance*, 28(2), 666–672.

Webster, S., Lin, H., Carter, F. M., III, Ehmann, K., & Cao, J. (2020). Physical mechanisms in hybrid additive manufacturing: a process design framework. *Journal of Materials Processing Technology*, 291, 117048.

Xiong, W., Mahadevan, S., & Guo, J. (2020). A hybrid model integrating physics-based simulation with machine learning for additive manufacturing process monitoring. *ASME Journal of Manufacturing Science and Engineering*, 143(6), 061008.

Yadroitsev, I., & Smurov, I. (2010). Selective laser melting technology: from the single laser melted track stability to 3D parts of complex shape. *Physics Procedia*, 5, 551–560.

Ye, D., Hong, G. S., Zhang, Y., Zhu, K., & Fuh, J. Y. H. (2018). Defect detection in selective laser melting technology by acoustic signals with deep belief networks. *International Journal of Advanced Manufacturing Technology*, 96(5-8), 2791–2801.

Yuan, B., Guss, G. M., Wilson, A. C., Hau-Riege, S. P., DePond, P. J., McMains, S., ... & Giera, B. (2019). Machine-learning-based monitoring of laser powder bed fusion. *Advanced Materials Technologies*, 3(12), 1800136.

Zhang, Y., Hong, G. S., Ye, D., Zhu, K., & Fuh, J. Y. H. (2021). Extraction and evaluation of melt pool, plume and spatter information for powder-bed fusion AM process monitoring. *Materials & Design*, 156, 458–469.

Zheng, B., Haley, J. C., Yang, N., Yee, J., Rubal, M., & Smugeresky, J. E. (2019). Investigation of Ni-based superalloy René 104 powder for additive manufacturing. *Metallurgical and Materials Transactions A*, 50(9), 4414–4427.

Zhu, Q., Liu, Z., & Yan, J. (2021). Machine learning for metal additive manufacturing: predicting temperature and melt pool fluid dynamics using physics-informed neural networks. *Computational Mechanics*, 67(2), 619–635.

Zou, J., Han, Y., So, J. I., Koh, K. H., & Ramanathan, S. (2020). Scanning strategy for reducing residual stress in selective laser melting. *Materials and Manufacturing Processes*, 36(14), 1869–1877.

---

*This literature review reflects knowledge of the field through early 2026. The field is advancing rapidly; readers are encouraged to consult recent issues of Additive Manufacturing, npj Computational Materials, and the International Journal of Machine Tools and Manufacture for the latest developments.*
