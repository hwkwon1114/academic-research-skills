---
name: deep-research
description: "Research agent team for ML-in-engineering research. Uses conditional routing: physics-heavy topics start with physics system, data acquisition, fidelity, and representation, while explicit method-comparison requests keep the direct method-family path. Supports research question formulation, methodology design, literature search, source verification, synthesis, and Socratic guidance for ML-assisted design, surrogates, Bayesian optimization, physics-informed ML, sim-to-real, multi-fidelity, transfer learning, and related engineering topics."
metadata:
 version: "3.0-ml-engineering"
 last_updated: "2026-04-11"
 status: active
 related_skills:
 - academic-paper
 - academic-pipeline
---

# Deep Research — Universal Academic Research Agent Team

Deep research tool for rigorous academic research on ML-for-engineering topics.

**v2.4** adds writing quality improvements to the report compiler:
- **Style Profile consumption** (optional) — If a Style Profile is available from academic-paper intake, the report compiler applies it as a soft guide for the Executive Summary and Synthesis sections. Discipline conventions and report objectivity take priority.
- **Writing Quality Check** — The report compiler runs a writing quality checklist before finalizing: flags AI-typical overused terms, checks sentence/paragraph length variation, removes throat-clearing openers. See `academic-paper/references/writing_quality_check.md`.

## Quick Start

**Physics-heavy / acquisition-first:**
```
I need literature on PDE/operator learning for fast data-efficient physics-model surrogates
```

**Method-first (keeps direct comparison path):**
```
Compare DeepONet, FNO, and PINNs for PDE surrogate learning
```

**Representation-sensitive:**
```
Help me study which representation works best for topology-changing physics surrogates
```

**Socratic mode:**
```
Guide my research: I want to use ML for structural optimization but I'm not sure
if representation, solver cost, or model family is the real bottleneck
```

**Routing policy:**
- **Physics-heavy** prompts ask first about the physics system, data source/acquisition path, fidelity ladder, representation, and evaluation/sim-to-real constraints before ML method choice.
- **Representation-sensitive** prompts ask representation questions first, even when they are not fully physics-heavy.
- **Explicit method-comparison** prompts keep the immediate method-family comparison path unless the user asks for broader scoping.
- **Generic / non-physics** prompts stay on the normal broad research flow.

**Execution:**
1. Scoping — Conditional intake + research question + methodology blueprint
2. Investigation — Systematic literature search + source verification + comparison bias
3. Analysis — Representation-aware front-end framing + model-family synthesis + DA checkpoint
4. Compilation — Markdown report with numbered references

---

## Trigger Conditions

### Trigger Keywords

**English**: research, deep research, literature review, systematic review, surrogate model, Bayesian optimization, Gaussian process, physics-informed, PINN, multi-fidelity, sim-to-real, transfer learning, domain adaptation, data-efficient design, ML-assisted design, design optimization, topology optimization, generative design, representation learning, mechanical engineering ML, computational design, fact-check, guide my research, help me think through, monitor this topic

### Socratic Mode Activation

Activate `socratic` mode when the user's **intent** matches any of the following patterns, **regardless of language**. Detect meaning, not exact keywords.

**Intent signals** (any one is sufficient):
1. User has no clear research question and wants guided thinking
2. User asks to be "led", "guided", or "mentored" through research
3. User expresses uncertainty about what to research or where to start
4. User wants to brainstorm, explore, or clarify a research direction
5. User describes a vague interest without a specific, answerable question

**Default rule**: When intent is ambiguous between `socratic` and `full`, **prefer `socratic`** — it is safer to guide first than to produce an unwanted report. The user can always switch to `full` later.

**Example triggers** (illustrative, not exhaustive):
"guide my research", "help me think through", or equivalent in any language

### Does NOT Trigger

| Scenario | Use Instead |
|----------|-------------|
| Writing a paper (not researching) | `academic-paper` |
| Reviewing a paper (structured review) | `academic-paper-reviewer` |
| Full research-to-paper pipeline | `academic-pipeline` |

### Quick Mode Selection Guide

| Your Situation | Recommended Mode |
|----------------|-----------------|
| Vague idea, need guidance | `socratic` |
| Physics-heavy topic, need full scoping + synthesis | `full` |
| Explicit method comparison or benchmark request | `quick` or `lit-review` |
| Need a quick brief | `quick` |
| Have a paper to evaluate before citing | `review` |
| Need model-family organized literature | `lit-review` |
| Need to verify specific claims | `fact-check` |

Not sure? Start with `socratic` -- it will help you figure out what you need.

---

## Agent Team (10 Agents)

| # | Agent | Role | Phase |
|---|-------|------|-------|
| 1 | `research_question_agent` | Classifies prompts as physics-heavy, representation-sensitive, method-first, or generic; shapes scoped research questions using the Research Scope Protocol and the correct intake order | Phase 1, Socratic Layers 1-3 |
| 2 | `research_architect_agent` | Designs methodology blueprint: physics/data/fidelity/representation-first for physics-heavy topics, representation-first for representation-sensitive topics, and direct Q1/Q2/Q3 method selection for method-first prompts | Phase 1 |
| 3 | `bibliography_agent` | Systematic literature search with retrieval ladder guidance and model-family annotated bibliography; assumption annotation per paper | Phase 2 |
| 4 | `source_verification_agent` | Evidence level grading (I-VII), venue/tier assessment, DOI/arXiv reference verification, reproducibility checklist | Phase 2 |
| 5 | `ml_comparison_bias_agent` | Comparison bias audit for papers making comparative claims: benchmark selection, hyperparameter fairness, metric bias, data leakage, compute budget asymmetry | Phase 2 (conditional: comparative papers only) |
| 6 | `synthesis_agent` | Preserves model-family synthesis as the backend: assumption chains, cross-family tradeoffs, sim-to-real audit, representation audit, gap analysis; receives bias trust scores from ml_comparison_bias_agent | Phase 3 |
| 7 | `report_compiler_agent` | Drafts markdown report with numbered references [1], [2]... (no APA formatting by default) | Phase 4 |
| 8 | `devils_advocate_agent` | DA Checkpoint 1 (after Phase 1): method-assumption fit, comparison completeness, representation coverage, evaluation scope, assumption verifiability. DA Checkpoint 2 (after Phase 3): landscape completeness, limitation root causes, validation accuracy, cross-family grounding, bottleneck attribution | Phase 1, 3, Socratic Layers 1, 2, 4 |
| 9 | `socratic_mentor_agent` | Guides engineering research thinking through 5 Socratic layers: problem characterization, method-assumption fit, validation design, failure mode examination, scope and generalizability | Socratic Mode (Layer 1-5) |
| 10 | `monitoring_agent` | Post-research literature monitoring: digests, retraction alerts, contradictory findings detection | Optional (post-pipeline) |

---

## Mode Selection Guide

See `references/mode_selection_guide.md` for the detailed guide.

**Routing pre-check before mode selection:**
- **Physics-heavy**: governing equations, PDE/operator learning, solver cost, multi-fidelity, simulation/experiment acquisition bottlenecks.
- **Representation-sensitive**: fields, meshes, graphs, operators, topology changes, encoding bottlenecks.
- **Method-first**: explicit `compare X vs Y`, benchmark, or architecture-ranking request.
- **Generic / non-physics**: broad research questions without the triggers above.

**Override rule:** explicit method-comparison requests override physics-heavy defaults unless the user asks for broader scoping.

```
User Input
 |
 +-- Already have text to review? --> review mode
 +-- Only need fact-checking? --> fact-check mode
 +-- Need guided thinking? --> socratic mode
 +-- Explicit method comparison? --> quick or lit-review mode
 +-- Physics-heavy / representation-sensitive topic? --> full mode (conditional intake in Phase 1)
 +-- Clear RQ, need comprehensive report? --> full mode
 +-- Need model-family organized literature? --> lit-review mode
 +-- Otherwise --> quick mode
```

---

## Orchestration Workflow (4 Phases)

```
User: "Research [topic]"
 |
=== Phase 1: SCOPING (Interactive) ===
 |
 |-> [research_question_agent] -> Routed RQ Brief
 | - Classify prompt: physics-heavy / representation-sensitive / method-first / generic
 | - If physics-heavy: ask physics system -> data source/acquisition path -> fidelity ladder
 |   -> representation -> evaluation/sim-to-real constraints before ML method choice
 | - If representation-sensitive: ask representation questions first, even without full solver/fidelity intake
 | - If method-first: provide immediate method-family framing; optional broader scoping is additive, not mandatory
 | - Research Scope Protocol scoring (Data Regime, Method Justification,
 |   Validation Design, Baseline Specificity, Scope Honesty)
 | - Scope boundaries (in-scope out-of-scope)
 | - Sim-to-real position statement
 | - 2-3 sub-questions
 |
 |-> [research_architect_agent] -> Methodology Blueprint
 | - For physics-heavy topics: cheapest usable data source, acquisition bottlenecks,
 |   fidelity ladder, representation choice, evaluation/sim-to-real constraints, then method selection
 | - For representation-sensitive topics: representation sufficiency + bottlenecks before method ranking
 | - For method-first prompts: direct Q1/Q2/Q3 method comparison path with lightweight context if needed
 | - Engineering baseline identification
 | - Assumptions list (with verifiability assessment)
 |
 +-> [devils_advocate_agent] -- CHECKPOINT 1
 | Reads references/ml_engineering_framework.md before running.
 | 5 abstract category checks:
 | - Method-assumption fit
 | - Comparison completeness (engineering baseline present?)
 | - Representation coverage
 | - Evaluation scope honesty
 | - Assumption verifiability
 | Verdict: PASS / REVISE (REVISE on items 1 or 2 blocks Phase 2)
 |
 ** User confirmation before Phase 2 **
 |
=== Phase 2: INVESTIGATION (Parallel) ===
 |
 |-> [bibliography_agent] -> Routed Annotated Bibliography
 | - LIVE SEARCH FIRST: use WebSearch + WebFetch (arXiv API, Semantic Scholar API)
 |   to retrieve 2024-2026 papers before drawing on training knowledge
 | - Retrieval ladder: fast current discovery first, then lineage, then canonical/manual full-text follow-up
 | - Systematic search strategy (databases, keywords, Boolean)
 | - Model-family organization remains the synthesis backend
 | - Per-paper annotation: method, key assumption, evaluation type,
 |   design representation, key finding, limitation root
 |
 |-> [source_verification_agent] -> Verified & Graded Sources
 | - Evidence hierarchy grading (Level I-VII)
 | - Venue/tier assessment (Tier 1-3)
 | - DOI/arXiv reference existence verification (100% coverage)
 | - Reproducibility checklist (code, dataset, hyperparameters, seeds, variance)
 |
 +-> [ml_comparison_bias_agent] -> Comparison Bias Verdicts
   - Activates only for papers making comparative claims (method A vs B)
   - 5 bias checks per paper: benchmark selection, hyperparameter fairness,
     metric bias, data leakage, compute budget asymmetry
   - Output: trust score (High / Moderate / Low / Unreliable) per paper
 |
=== Phase 3: ANALYSIS ===
 |
 |-> [synthesis_agent] -> Representation-Aware Framing + Model-Family Synthesis
 | - Reads ml_comparison_bias_agent trust scores; flags Low/Unreliable papers
 | - Preserves model-family clustering as the stable backend
 | - For physics-heavy domains, front-load physics regime, acquisition path, fidelity,
 |   and representation bottlenecks before cross-family comparison
 | - Assumption inheritance chains (foundational -> generalized)
 | - Cross-family tradeoffs (where families are composable vs. incompatible)
 | - Sim-to-real audit (simulation-only vs. hardware-validated)
 | - Representation audit (what design encodings are used; topology limits)
 | - Gap analysis (what problem areas have no ML literature)
 |
 +-> [devils_advocate_agent] -- CHECKPOINT 2
   Reads references/ml_engineering_framework.md before running.
   5 abstract category checks:
   - Landscape completeness (families missing? papers misclassified?)
   - Limitation root cause depth (surface description vs. actual assumption violation?)
   - Validation claim accuracy (evidence type matches what was demonstrated?)
   - Cross-family synthesis grounding (relationships backed by paper evidence?)
   - Performance bottleneck attribution (ML method vs. representation encoding?)
   Verdict: PASS / REVISE (REVISE on items 1-3 requires synthesis re-run before Phase 4)
 |
=== Phase 4: COMPILATION ===
 |
 +-> [report_compiler_agent] -> Markdown Report + Numbered References
   - Default output: plain markdown, references as [1], [2] inline and at end
   - No title page, no APA formatting (user may request IEEE/ASME at intake)
   - Sections: Introduction, Method-Family Literature, Assumption Map,
     Sim-to-Real Summary, Representation Audit, Gap Analysis, References
   - Self-review before finalizing: all families present? gap analysis
     connected to family limitations? references consistent with inline citations?
```

### Checkpoint Rules

1. **Devil's Advocate** has 2 mandatory checkpoints (Phases 1 and 3); **Critical-severity** issues block progression
2. A REVISE verdict on DA Checkpoint 1 items 1 or 2 (method-assumption fit, comparison completeness) blocks Phase 2
3. A REVISE verdict on DA Checkpoint 2 items 1-3 requires synthesis_agent to re-run affected sections before Phase 4
4. User confirmation required after Phase 1 before proceeding

---

## Socratic Mode: GUIDED RESEARCH DIALOGUE

Core principle: From the perspective of a Q1 international journal editor-in-chief, guide users to clarify their research questions through Socratic questioning. Never give direct answers; instead, use follow-up questions to help users think through the issues themselves.

See `agents/socratic_mentor_agent.md` for the detailed agent definition.
See `references/socratic_questioning_framework.md` for the questioning framework.

```
User: "Guide my research on [topic]"
 |
=== Layer 1: PROBLEM CHARACTERIZATION ===
 |
 +-> [socratic_mentor_agent] -> Establish the engineering design context
 [research_question_agent] -> Research Scope Protocol guidance (data regime)
 [devils_advocate_agent] -> Challenge whether problem framing implies clear data regime
 - "What is the design task? What makes each evaluation expensive?"
 - "What does success look like in engineering terms -- not model accuracy?"
 Extract [INSIGHT: ...] each round
 At least 2 rounds of dialogue before entering Layer 2
 |
=== Layer 2: METHOD-ASSUMPTION FIT ===
 |
 +-> [socratic_mentor_agent] -> Connect ML method to problem characteristics
 [research_question_agent] -> Research Scope Protocol guidance (method justification)
 [devils_advocate_agent] -> Challenge method-assumption fit at end of Layer 2
 - "What assumption does your chosen method make about the response landscape?"
 - "What would a practicing engineer use without ML? That's your baseline."
 At least 2 rounds of dialogue before entering Layer 3
 |
=== Layer 3: VALIDATION DESIGN ===
 |
 +-> [socratic_mentor_agent] -> Establish validation scope and sim-to-real position
 [research_question_agent] -> Research Scope Protocol guidance (validation design)
 - "Simulation-only or hardware-validated? What justifies that scope?"
 - "Is your metric the same as the engineering objective, or a proxy?"
 At least 2 rounds of dialogue before entering Layer 4
 |
=== Layer 4: FAILURE MODE EXAMINATION ===
 |
 +-> [socratic_mentor_agent] -> Force concrete thinking about when the approach breaks
 [devils_advocate_agent] -> Challenge failure mode assessment
 - "Under what conditions does your method's key assumption get violated?"
 - "What physical phenomena does your simulation omit that could matter on hardware?"
 At least 2 rounds of dialogue before entering Layer 5
 |
=== Layer 5: SCOPE AND GENERALIZABILITY ===
 |
 +-> [socratic_mentor_agent] -> Bound what the study can claim
 - "What specific design families and conditions does your study cover?"
 - "Is there a generalization claim the evaluation cannot actually support?"
 At least 1 round of dialogue
 |
 +-> Compile all [INSIGHT]s into Research Plan Summary
 Can directly hand off to academic-paper (plan mode)
```

### Socratic Mode Dialogue Management Rules

- At least 2 rounds of dialogue per layer before moving to the next (Layer 5 requires at least 1)
- Users can request to skip to the next layer at any time
- Mentor responses limited to 200-400 words
- If no convergence after 10 rounds -> suggest switching to `full` mode (see Failure Paths F6)
- If dialogue exceeds 15 rounds -> automatically compile INSIGHTs and end
- If user requests direct answers -> gently decline, explain the value of guided learning

---

## Operational Modes

| Mode | Agents Active | Output | Length |
|------|---------------|--------|--------|
| `full` (default) | RQ + Architect + DA(x2) + Biblio + Verification + Bias + Synthesis + Report | Markdown report, numbered references | 3,000-8,000 words |
| `quick` | RQ + Biblio + Verification + Report | Research brief (markdown) | 500-1,500 words |
| `review` | Devil's Advocate + Source Verification | Reviewer report on provided text | N/A |
| `lit-review` | Biblio + Verification + Bias + Synthesis | Annotated bibliography + model-family synthesis | 1,500-4,000 words |
| `fact-check` | Source Verification only | Verification report per claim | 300-800 words |
| `socratic` | Socratic Mentor + RQ + Devil's Advocate | Research Plan Summary (INSIGHT collection) | N/A (iterative) |

---

## Failure Paths

See `references/failure_paths.md` for all failure scenarios, trigger conditions, and recovery strategies across all modes.

Key failure path summary:

| Failure Scenario | Trigger Condition | Recovery Strategy |
|---------|---------|---------|
| RQ scope too broad | Research Scope Protocol average < 2.5 | Return to Phase 1, narrow to specific design domain + data regime |
| Method-assumption mismatch | DA Checkpoint 1 REVISE on item 1 | Return to Phase 1; justify method from Q1/Q2/Q3 framework |
| No engineering baseline | DA Checkpoint 1 REVISE on item 2 | Return to Phase 1; identify what a practicing engineer would use |
| Insufficient literature | bibliography_agent finds < 5 sources | Expand search strategy, adjacent keywords, broader design family |
| DA Checkpoint CRITICAL | Fatal assumption violation or missing baseline | STOP, explain issue, require correction before Phase 2 |
| Socratic non-convergence | > 10 rounds in a layer without convergence | Suggest switching to `full` mode |
| User abandons mid-process | Explicitly states they don't want to continue | Save progress, provide re-entry path |
| All papers simulation-only | No hardware-validated papers in corpus | Note in synthesis; flag as gap; do not allow hardware claims |

---

## Literature Monitoring (Optional Post-Pipeline)

After any research mode is complete, users can optionally activate the `monitoring_agent` to set up post-research literature monitoring. This is not part of the main pipeline — it is an auxiliary capability triggered on demand.

See `agents/monitoring_agent.md` for the detailed agent definition.
See `references/literature_monitoring_strategies.md` for platform-specific setup guides.

**Trigger**: "monitor this topic", "set up alerts", "track new publications on this"

**Capabilities**:
- Weekly/monthly monitoring digest generation
- Retraction alerts for cited sources
- Contradictory findings detection
- Key author tracking
- Keyword evolution tracking

**Input**: Completed bibliography + search strategy from any research mode
**Output**: Monitoring configuration + digest template (markdown)

**Limitation**: The monitoring agent produces configurations and templates for the user to act on. It cannot run autonomous background monitoring.

---

## Handoff Protocol: deep-research → academic-paper

After research is complete, the following materials can be handed off to `academic-paper`:

1. **Research Question Brief** (from research_question_agent)
2. **Methodology Blueprint** (from research_architect_agent)
3. **Annotated Bibliography** (from bibliography_agent)
4. **Synthesis Report** (from synthesis_agent)
5. **[If socratic mode] INSIGHT Collection and Research Plan Summary**

**Trigger**: User says "now help me write a paper" or "write a paper based on this"

`academic-paper`'s `intake_agent` will automatically detect available materials and skip redundant steps:
- Has RQ Brief -> skip topic scoping
- Has Bibliography -> skip literature search
- Has Synthesis -> accelerate findings discussion writing

See `examples/handoff_to_paper.md` for a detailed handoff example.

---

## Full Academic Pipeline

See `academic-pipeline/SKILL.md` for the complete workflow.

---

## Agent File References

| Agent | Definition File |
|-------|----------------|
| research_question_agent | `agents/research_question_agent.md` |
| research_architect_agent | `agents/research_architect_agent.md` |
| bibliography_agent | `agents/bibliography_agent.md` |
| source_verification_agent | `agents/source_verification_agent.md` |
| ml_comparison_bias_agent | `agents/ml_comparison_bias_agent.md` |
| synthesis_agent | `agents/synthesis_agent.md` |
| report_compiler_agent | `agents/report_compiler_agent.md` |
| devils_advocate_agent | `agents/devils_advocate_agent.md` |
| socratic_mentor_agent | `agents/socratic_mentor_agent.md` |
| monitoring_agent | `agents/monitoring_agent.md` |

---

## Reference Files

| Reference | Purpose | Used By |
|-----------|---------|---------|
| `references/ml_engineering_framework.md` | ML method selection guide (data regime -> method family), assumption catalog (GP, NN, PINN, multi-fidelity, BO, domain adaptation), sim-to-real gap taxonomy, representation taxonomy, 5 common research patterns with key papers | research_architect, synthesis, devils_advocate (Checkpoints 1+2), bibliography |
| `references/logical_fallacies.md` | 30+ fallacies catalog | devils_advocate |
| `references/socratic_questioning_framework.md` | 6 types of Socratic questions + prompt patterns | socratic_mentor |
| `references/failure_paths.md` | Failure scenarios with triggers and recovery paths | all agents |
| `references/mode_selection_guide.md` | Mode selection flowchart and comparison table | orchestrator |
| `references/literature_monitoring_strategies.md` | Google Scholar alerts, RSS feeds, citation tracking, monitoring cadence | monitoring_agent |

---

## Templates

| Template | Purpose |
|----------|---------|
| `templates/research_brief_template.md` | Quick mode output format |
| `templates/literature_matrix_template.md` | Model-family x Assumption analysis matrix |
| `templates/evidence_assessment_template.md` | Per-source quality assessment card |

---

## Examples

| Example | Demonstrates |
|---------|-------------|
| `examples/socratic_guided_research.md` | Complete Socratic mode multi-turn dialogue with engineering layers |
| `examples/handoff_to_paper.md` | deep-research full mode handoff to academic-paper |
| `examples/fact_check_mode.md` | Fact-check mode: source verification with per-claim verdicts |

---

## Output Language

English. Academic terminology in English. Socratic mode uses natural conversational style.

---

## Quality Standards

1. **Every claim must have a citation** -- no unsupported assertions
2. **Evidence hierarchy (ML/Engineering)** -- formal proofs + empirical validation > comprehensive ablations > multi-method benchmarks > single-benchmark studies > simulation-only demonstrations > expert opinion. See `agents/source_verification_agent.md` for full levels.
3. **Method selection must be justified** -- every ML method choice must cite specific problem characteristics (data regime, evaluation cost, uncertainty requirements). See `references/ml_engineering_framework.md`.
4. **Assumptions must be traced to limitations** -- limitations in a paper are almost always traceable to a specific model assumption. Surface these explicitly.
5. **Sim-to-real status must be documented** -- for every paper: simulation only, hardware validated, or both.
6. **Literature organized by model family** -- papers sharing a mathematical lineage go together in synthesis and bibliography outputs.
7. **Reproducibility** -- search strategies, inclusion criteria, and analytical methods must be documented for replication.
8. **Socratic integrity** -- in socratic mode, never give direct answers; always guide through questions.

## Cross-Agent Quality Alignment

Unified definitions to prevent inconsistency across agents:

| Concept | Definition | Applies To |
|---------|-----------|------------|
| **Peer-reviewed** | Published in a journal with formal peer review. Conference proceedings count if explicitly peer-reviewed (NeurIPS/ICML/ICRA = yes; workshops = varies). arXiv = treat as unreviewed Tier 2. | bibliography_agent, source_verification_agent |
| **Currency Rule** | By domain: ML/deep learning = 3 years, Bayesian optimization/GP = 5 years, FEM/CFD/structural engineering = 10 years. Seminal works exempt regardless of age. | bibliography_agent |
| **CRITICAL severity** | Issue that, if unresolved, would invalidate a core conclusion. Requires immediate resolution before pipeline proceeds. | All agents |
| **Source Tier** | Tier 1 = NeurIPS/ICML/ICRA/ASME/AIAA top journals; Tier 2 = other peer-reviewed engineering/ML venues; Tier 3 = arXiv preprints from established groups | bibliography_agent, source_verification_agent |
| **Minimum Source Count** | full = 15+, quick = 5-8, lit-review = 20+ | bibliography_agent |
| **Verification Threshold** | 100% DOI/arXiv check + 50% WebSearch spot-check | source_verification_agent |
| **Comparative claim** | Any paper that benchmarks 2+ methods against each other -- triggers ml_comparison_bias_agent | ml_comparison_bias_agent |

> **Cross-Skill Reference**: See `shared/handoff_schemas.md` for inter-stage data exchange formats.

---

## Integration with Other Skills

```
deep-research + academic-paper -> Full research-to-publication pipeline (ML/engineering focus)
deep-research (socratic) + academic-paper (plan) -> Guided research + paper planning
deep-research (lit-review) -> Model-family organized bibliography for standalone use
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 3.1 | 2026-04-05 | 6-phase pipeline collapsed to 4 phases (removed editor_in_chief, ethics_review, DA Checkpoint 3, Phase 6 revision loop -- all redundant with upstream validation). Added ml_comparison_bias_agent (Phase 2, parallel, conditional on comparative claims). Trimmed source_verification_agent to venue/tier + reference existence + reproducibility only (bias assessment moved to new agent). Rewrote all 5 Socratic layers for ML/engineering context (problem characterization, method-assumption fit, validation design, failure mode examination, scope and generalizability). Replaced FINER/PICOS in research_question_agent with Research Scope Protocol (data regime, method justification, validation design, baseline specificity, scope honesty). Default output changed to plain markdown with numbered references (not APA 7.0). Removed systematic-review mode (PRISMA/RoB/GRADE not applicable to ML/engineering). |
| 2.4 | 2026-03-27 | Report compiler now consumes optional Style Profile (from academic-paper intake) and runs Writing Quality Check checklist before finalizing reports. Style Profile applied as soft guide for Executive Summary and Synthesis sections; discipline conventions take priority. Writing Quality Check catches overused AI-typical terms, em dash overuse, throat-clearing openers, and monotonous sentence rhythm. See `academic-paper/references/writing_quality_check.md` and `shared/style_calibration_protocol.md` |
| 2.3 | 2026-03-08 | Added systematic-review mode (7th mode): PRISMA 2020 compliant pipeline with risk_of_bias_agent (RoB 2 + ROBINS-I), meta_analysis_agent (effect sizes, heterogeneity, GRADE, narrative synthesis), 2 new templates (PRISMA protocol + report), systematic_review_toolkit reference. Added monitoring_agent (post-pipeline literature monitoring with digests, retraction alerts, author tracking) + literature_monitoring_strategies reference. Enhanced socratic_mentor_agent with 4 convergence signals, 4-type question taxonomy, and auto-end triggers. Added Quick Mode Selection Guide to SKILL.md |
| 2.2 | 2025-03-05 | Added synthesis anti-patterns, Socratic quantified thresholds & auto-end conditions, reference existence verification (DOI + WebSearch), enhanced ethics reference integrity check (50% + Retraction Watch), mode transition matrix, cross-agent quality alignment definitions |
| 2.1 | 2026-03 | Added IRB decision tree, EQUATOR reporting guidelines, preregistration guide + template; enhanced ethics_review_agent with human subjects dimension; enhanced research_architect_agent with ethics/EQUATOR/preregistration integration; enhanced methodology_patterns with EQUATOR cross-references |
| 2.0 | 2026-02 | Added socratic mode (10th agent), failure paths, mode selection guide, handoff protocol, 2 new examples, 3 new references |
| 1.0 | 2026-02 | Initial release: 9 agents, 5 modes, 6-phase pipeline |
