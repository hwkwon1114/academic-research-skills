# Live arXiv Search Test Results

**Date**: 2026-04-07
**Purpose**: Verify that live arXiv API + ar5iv can retrieve papers beyond training knowledge cutoff

---

## Search 1: Titles containing "additive manufacturing" AND "machine learning"

Query: `ti:"additive manufacturing" AND ti:"machine learning"` — sorted by submission date descending

| Submitted | arXiv ID | Title |
|-----------|----------|-------|
| 2026-03-15 | 2603.14489 | Predicting Stress-strain Behaviors of Additively Manufactured Materials via Loss-based... |
| 2025-09-15 | 2509.16233 | Comparison of Deterministic and Probabilistic Machine Learning Algorithms for Precise... |
| 2025-09-01 | 2509.01769 | AM-DefectNet: Additive Manufacturing Defect Classification Using Machine Learning |
| 2025-05-02 | 2505.01424 | Computational, Data-Driven, and Physics-Informed Machine Learning Approaches for Microstructure... |
| 2025-04-30 | 2504.21317 | Redundancy Analysis and Mitigation for Machine Learning-Based Process Monitoring of AM |
| 2025-01-15 | 2501.08922 | Discovery of Spatter Constitutive Models in Additive Manufacturing Using Machine Learning |
| 2024-08-09 | 2408.05307 | Audio-visual cross-modality knowledge transfer for machine learning-based in-situ monitoring |
| 2024-07-15 | 2407.10761 | Physics-Informed Machine Learning for Smart Additive Manufacturing |

## Search 2: Titles containing "additive manufacturing" AND "deep learning"

| Submitted | arXiv ID | Title |
|-----------|----------|-------|
| 2026-03-14 | 2603.13831 | Efficient Semi-Automated Material Microstructure Analysis Using Deep Learning |
| 2025-07-10 | 2507.07757 | Deep Learning based 3D Volume Correlation for Additive Manufacturing |
| 2024-10-31 | 2410.24055 | Advanced Predictive Quality Assessment for Ultrasonic AM with Deep Learning |
| 2024-08-05 | 2408.02427 | Attenuation-adjusted deep learning of pore defects in 2D radiographs of AM |

---

## Sample Paper Extraction via arxiv.org Abstract Page

**Paper**: 2504.21317 — "Redundancy Analysis and Mitigation for ML-Based Process Monitoring of AM"
**Submitted**: 2025-04-30

**Abstract (extracted live)**:
> The deployment of machine learning (ML)-based process monitoring systems has significantly advanced additive manufacturing (AM) by enabling real-time defect detection, quality assessment, and process optimization. However, redundancy is a critical yet often overlooked challenge in the deployment and operation of ML-based AM process monitoring systems. Excessive redundancy leads to increased equipment costs, compromised model performance, and high computational requirements, posing barriers...

**Extraction method**: `https://arxiv.org/abs/2504.21317` — abstract extracted from HTML meta tags ✓
**ar5iv status**: Page renders (47KB HTML) but abstract regex needs tuning; use `arxiv.org/abs/ID` for metadata, `ar5iv.labs.arxiv.org/html/ID` for full paper body.

---

## Assessment

**Live search successfully retrieves papers beyond training knowledge cutoff**: YES

Papers from 2025 and 2026 were retrieved and verified:
- 2026-03-15 paper confirmed live
- Multiple 2025 papers (2025-09, 2025-07, 2025-05, 2025-04, 2025-01) retrieved with correct titles

**Working URL patterns**:
- arXiv API (title search): `https://export.arxiv.org/api/query?search_query=ti:"term1"+AND+ti:"term2"&max_results=N&sortBy=submittedDate&sortOrder=descending`
- Paper abstract: `https://arxiv.org/abs/ARXIV_ID` — extract from `citation_abstract` meta tag
- Paper full text: `https://ar5iv.labs.arxiv.org/html/ARXIV_ID` — HTML render of full paper

**Rate limiting**: arXiv API returns 429 if queried too rapidly. Wait 10-15s between queries. No API key required for basic access.

**Limitation**: ar5iv HTML structure varies by paper; use `arxiv.org/abs/ID` for reliable metadata extraction, ar5iv for reading full method/results sections.
