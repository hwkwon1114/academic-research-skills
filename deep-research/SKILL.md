---
name: deep-research
description: "Two-mode literature-review and cross-field research-direction skill for engineering researchers. `socratic` narrows the research frame (engineering domain, method family, open problem). `lit-review` produces an engineering-framed literature synthesis with per-paper assumption/outputs/gaps blocks and a 3-direction Research Agenda for applying/improving methods from other fields. Triggers on: research, literature review, lit review, deep research, guide my research, research agenda, cross-field application, apply method from other field, find research direction, surrogate model, Bayesian optimization, physics-informed, PINN, multi-fidelity, sim-to-real, transfer learning, ML-assisted design, topology optimization."
metadata:
 version: "4.0-engineering-application"
 last_updated: "2026-04-24"
 status: active
---

# deep-research — Engineering Lit-Review and Cross-Field Research Direction

A two-mode skill for engineering researchers who want to find where methods from other fields can be applied or improved in their domain — not to invent new algorithms, but to identify the right cross-field application opportunities.

## Quick Start

**Socratic mode** (start here if your research frame is unclear):
```
Guide my research: I want to apply ML to structural optimization but I'm not sure
which method family fits my data regime or what the real performance gap is.
```
Socratic asks ≥3 narrowing questions (engineering domain → method family → open problem), then emits a Research Frame and a handoff prompt. **No auto-invoke** — you decide when to run lit-review.

**Lit-review mode** (use when you have a converged Research Frame):
```
Run lit-review. Here is my Research Frame:
- engineering_domain: topology optimization for aerospace structures
- method_family_of_interest: Bayesian optimization
- open_problem: discrete design variables break GP surrogate assumptions
- ...
```
Produces: per-paper summary blocks (assumptions / outputs / gaps / cross-field transfer potential) + Research Agenda (3 ranked directions: Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]).

---

## Trigger Keywords

**English**: research, literature review, lit review, deep research, guide my research, research agenda, cross-field application, apply method from other field, find research direction, research direction, surrogate model, Bayesian optimization, Gaussian process, physics-informed, PINN, multi-fidelity, sim-to-real, transfer learning, domain adaptation, data-efficient design, ML-assisted design, design optimization, topology optimization, generative design, representation learning, computational design, monitor this topic

### Socratic Mode Activation

Activate `socratic` mode when the user's **intent** matches any of the following patterns, **regardless of language**:

1. User has no clear research question and wants guided thinking
2. User asks to be "led", "guided", or "mentored" through research
3. User expresses uncertainty about what to research or where to start
4. User wants to brainstorm or clarify a research direction
5. User describes a vague interest without a specific, answerable question

**Default rule**: When intent is ambiguous between `socratic` and `lit-review`, **prefer `socratic`** — it is safer to guide first than to produce an unwanted report.

### Quick Mode Selection Guide

| Your Situation | Recommended Mode |
|----------------|-----------------|
| Unclear research frame, unsure what to study | `socratic` |
| Have a converged Research Frame, ready for literature | `lit-review` |

**Socratic is a prerequisite for lit-review unless the user already has a Research Frame.**

---

## Agent Team (11 Agents)

| # | Agent | Socratic | Lit-review | Role |
|---|-------|----------|------------|------|
| 1 | `research_question_agent` | ✓ (Layers 1-3) | ✓ (Phase 1) | Classifies prompt; shapes research questions; Research Scope Protocol |
| 2 | `research_architect_agent` | — | ✓ (Phase 1) | Designs methodology blueprint; baseline identification; assumption list |
| 3a | `paper_fetch_agent` | — | ✓ (Phase 2) | Full-text retrieval ladder (arxiv → ar5iv → OpenAlex → Unpaywall → S2 → metadata-only) |
| 3 | `bibliography_agent` | — | ✓ (Phase 2) | Systematic literature search; per-paper extracted_claims[] blocks when full-text available |
| 4 | `source_verification_agent` | — | ✓ (Phase 2) | Evidence level grading (I-VII); venue/tier; DOI/arXiv verification; reproducibility checklist |
| 5 | `ml_comparison_bias_agent` | — | ✓ (Phase 2, conditional) | Comparison bias audit for papers making comparative claims |
| 6 | `synthesis_agent` | — | ✓ (Phase 3) | Assumption chains; cross-family tradeoffs; sim-to-real audit; representation audit; gap analysis |
| 7 | `report_compiler_agent` | — | ✓ (Phase 4) | Engineering-framed lit-review report: per-paper blocks + Research Agenda + PDF conversion |
| 8 | `devils_advocate_agent` | ✓ (Layers 2, 4) | ✓ (Phases 1, 3) | DA Checkpoint 1 (Phase 1): method-assumption fit. DA Checkpoint 2 (Phase 3): landscape completeness |
| 9 | `socratic_mentor_agent` | ✓ (Layers 1-5) | — | Guides through 5 Socratic layers; emits Research Frame on convergence |
| 10 | `monitoring_agent` | — | optional | Post-research literature monitoring: digests, retraction alerts, contradictory findings |

---

## Mode Selection Guide

See `references/mode_selection_guide.md` for the detailed guide.

```
User Input
 |
 +-- Already have a converged Research Frame? --> lit-review
 +-- Unclear frame, want guided thinking?    --> socratic (emits Frame + user-confirmation prompt — no auto-chain)
```

**No auto-invoke from Socratic to lit-review.** Socratic always ends by printing a user-confirmation handoff prompt. The user must explicitly run lit-review (by pasting the Frame or typing "run lit-review").

---

## Orchestration Workflow

### Socratic Mode

```
User: "Guide my research on [topic]"
 |
=== Layer 1: PROBLEM CHARACTERIZATION ===
 +-> socratic_mentor_agent — ≥1 question narrowing ENGINEERING DOMAIN
     research_question_agent — Research Scope Protocol guidance
     devils_advocate_agent — challenge problem framing
     Exit: design task + data regime + evaluation cost + engineering success criterion + explicit domain
 |
=== Layer 2: METHOD-ASSUMPTION FIT ===
 +-> socratic_mentor_agent — ≥1 question narrowing METHOD FAMILY + ≥1 question naming SOURCE FIELD
     research_question_agent — Research Scope Protocol guidance
     devils_advocate_agent — challenge method-assumption fit
     Exit: method family + key assumption + data regime match + named source field + engineering baseline
 |
=== Layer 3: VALIDATION DESIGN ===
 +-> socratic_mentor_agent — ≥1 question naming OPEN PROBLEM / performance gap
     research_question_agent — Research Scope Protocol guidance
     Exit: validation scope + sim-to-real position + evaluation metric + open problem stated
 |
=== Layer 4: FAILURE MODE EXAMINATION ===
 +-> socratic_mentor_agent — force concrete thinking about breakdown conditions
     devils_advocate_agent — challenge failure mode assessment
     Exit: ≥2 concrete failure conditions named
 |
=== Layer 5: SCOPE AND GENERALIZABILITY ===
 +-> socratic_mentor_agent — bound what the study can claim
     Exit: scope boundary stated; what is and is not demonstrated
 |
 +-> Emit RESEARCH FRAME (standalone fenced Markdown block)
     Print user-confirmation handoff prompt:
     "Your Research Frame is ready. Next step: run lit-review with this Frame —
      paste this block into a new prompt or type 'run lit-review'."
```

### Lit-review Mode

```
User: "Run lit-review" + Research Frame (from Socratic or user-supplied)
 |
=== Phase 1: SCOPING ===
 +-> research_question_agent → Routed RQ Brief (from Research Frame)
 +-> research_architect_agent → Methodology Blueprint
 +-> devils_advocate_agent — CHECKPOINT 1 (method-assumption fit, comparison completeness, etc.)
     ** User confirmation before Phase 2 **
 |
=== Phase 2: INVESTIGATION (Parallel) ===
 +-> paper_fetch_agent → per-paper full text (or honest abstract-only)
 +-> bibliography_agent → Annotated Bibliography (live search first, then lineage)
 +-> source_verification_agent → Verified & Graded Sources
 +-> ml_comparison_bias_agent → Comparison Bias Verdicts (conditional: comparative papers only)
 |
=== Phase 3: ANALYSIS ===
 +-> synthesis_agent → Method-Family Synthesis + Gap Analysis
 +-> devils_advocate_agent — CHECKPOINT 2 (landscape completeness, limitation root causes, etc.)
 |
=== Phase 4: COMPILATION ===
 +-> report_compiler_agent → Lit-Review Report (Markdown)
     — per-paper summary blocks (Assumptions / Outputs / Gaps / Cross-Field Transfer Potential)
     — Research Agenda (exactly 3 ranked directions with qualitative labels)
     — POST-EMISSION: lit_review_validate.py (automatic, blocks on failure)
     — PDF conversion: md_to_pdf.py (or Markdown-only with loud install-message warning)
```

---

## Socratic Mode: Narrowing Requirements

Core principle: guide users to clarify their research frames through Socratic questioning. Never give direct answers.

See `agents/socratic_mentor_agent.md` for the detailed agent definition.
See `references/socratic_questioning_framework.md` for the questioning framework.

**Minimum narrowing questions (total across the session, covering all three):**
1. **Engineering domain** — what specific engineering field and design task? (Layer 1)
2. **Method family** — what ML/computational method family, from what source field? (Layer 2)
3. **Open problem** — what specific unsolved problem or performance gap? (Layer 3)

On convergence, Socratic emits a Research Frame as a standalone fenced Markdown block matching `references/research_frame_schema.md` (10 fields including `failure_modes[]` and `scope_boundaries[]`), then prints:
> "Your Research Frame is ready. Next step: run lit-review with this Frame — paste this block into a new prompt or type 'run lit-review'."

**No auto-chain.** The user must explicitly invoke lit-review.

---

## Operational Modes

| Mode | Agents Active | Output | Length |
|------|---------------|--------|--------|
| `socratic` | Socratic Mentor + RQ + Devil's Advocate | Research Frame (fenced Markdown block) + user-confirmation handoff prompt | N/A (iterative) |
| `lit-review` | RQ + Architect + DA(×2) + PaperFetch + Biblio + Verification + Bias + Synthesis + Report Compiler | Markdown lit-review report + PDF (if pandoc available) | 3,000–8,000 words |

---

## Response Envelope: `deep-research-agents-used:` marker

Every invocation MUST emit, in the response prologue, a single grep-friendly line:

```
deep-research-agents-used: [agent_1, agent_2, ...]
```

Rules:
1. List every agent that actually invoked code or made a network call.
2. Use agent slug names from the Agent Team table.
3. Order is the order of first invocation.
4. Emit the line even on partial runs.

---

## Failure Paths

See `references/failure_paths.md` for all failure scenarios.

| Failure Scenario | Trigger Condition | Recovery Strategy |
|---------|---------|---------|
| RQ scope too broad | Research Scope Protocol average < 2.5 | Return to Phase 1, narrow to specific domain + data regime |
| Method-assumption mismatch | DA Checkpoint 1 REVISE on item 1 | Return to Phase 1; justify method from Q1/Q2/Q3 framework |
| No engineering baseline | DA Checkpoint 1 REVISE on item 2 | Return to Phase 1; identify what a practicing engineer would use |
| Insufficient literature | bibliography_agent finds < 5 sources | Expand search strategy, adjacent keywords, broader design family |
| DA Checkpoint CRITICAL | Fatal assumption violation or missing baseline | STOP, explain issue, require correction before Phase 2 |
| Socratic non-convergence | > 10 rounds in a layer without convergence | Suggest re-running with a narrower starting question |
| Validator failure | lit_review_validate.py exits non-zero | Report validator stderr to user; do not claim completion |
| PDF toolchain absent | pandoc not found | Save Markdown, print install message, exit 2 |

---

## Literature Monitoring (Optional Post-Pipeline)

After any lit-review run, users can optionally activate `monitoring_agent` for post-research monitoring.

**Trigger**: "monitor this topic", "set up alerts", "track new publications on this"

See `agents/monitoring_agent.md` and `references/literature_monitoring_strategies.md`.

---

## Agent File References

| Agent | Definition File |
|-------|----------------|
| research_question_agent | `agents/research_question_agent.md` |
| research_architect_agent | `agents/research_architect_agent.md` |
| paper_fetch_agent | `agents/paper_fetch_agent.md` |
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
| `references/ml_engineering_framework.md` | ML method selection guide; assumption catalog; sim-to-real taxonomy; representation taxonomy | research_architect, synthesis, devils_advocate, bibliography |
| `references/logical_fallacies.md` | 30+ fallacies catalog | devils_advocate |
| `references/socratic_questioning_framework.md` | 6 types of Socratic questions + prompt patterns | socratic_mentor |
| `references/failure_paths.md` | Failure scenarios with triggers and recovery paths | all agents |
| `references/mode_selection_guide.md` | Mode selection flowchart (2-mode: socratic / lit-review) | orchestrator |
| `references/literature_monitoring_strategies.md` | Google Scholar alerts, RSS feeds, citation tracking | monitoring_agent |
| `references/research_frame_schema.md` | Research Frame schema (10 fields) for Socratic → lit-review handoff | socratic_mentor, report_compiler |
| `references/handoff_schemas.md` | All internal data contracts (Schemas 1–4) | all agents |
| `references/cross_model_verification.md` | Optional cross-model verification protocol | source_verification, devils_advocate |

---

## Bundled Scripts

| Script | Used by | Purpose |
|--------|---------|---------|
| `scripts/paper_fetch.py` | `paper_fetch_agent`, `source_verification_agent` | Full retrieval ladder (arxiv → ar5iv → OpenAlex → Unpaywall → S2 → metadata-only). Returns YAML with `text`, `retrieval_quality`, `fetch_log`. |
| `scripts/arxiv_search.py` | `bibliography_agent` | arXiv API discovery with rate-limit floor and `--from <year>` filter. |
| `scripts/slugify.py` | `report_compiler_agent` | Deterministic noun-phrase → kebab-case slug. |
| `scripts/ref_verify.py` | `source_verification_agent` | DOI/arXiv existence check via Crossref + arXiv Atom API. |
| `scripts/s2_citations.py` | `bibliography_agent` | Forward/backward citation graph via Semantic Scholar Graph API. |
| `scripts/vault_lint.py` | `report_compiler_agent` | Pre-flight lint on staging bundles (vault mode, legacy). |
| `scripts/bias_signals.py` | `ml_comparison_bias_agent` | Structural-indicator gatherer for 5 bias checks; regex pattern families on paper body. |
| `scripts/md_to_pdf.py` | `report_compiler_agent` | Convert Markdown report to PDF via pandoc (primary) or weasyprint (optional lazy import). On pandoc-missing: print install-message sentinel and exit 2. |
| `scripts/lit_review_validate.py` | `report_compiler_agent` (automatic, post-emission) | **Invoked automatically by `report_compiler_agent` after Markdown emission. Blocks completion on failure.** Checks: (1) per-paper block schema present for every key paper; (2) exactly 3 Research Agenda directions with qualitative labels (`highest tractable`, `medium`, `stretch-exploratory`); (3) each direction's first non-blank line matches the Apply/improve template; (4) both `.md` and `.pdf` files exist on disk, or Markdown-only with the install-message string in stderr; (5) Research Frame section present with all 10 schema fields. |

---

## Examples

| Example | Demonstrates |
|---------|-------------|
| `examples/socratic_guided_research.md` | Socratic mode multi-turn dialogue → Research Frame → user-confirmation handoff prompt |
| `examples/lit_review_with_agenda.md` | Complete lit-review: Research Frame intake → per-paper blocks → 3-direction Research Agenda (canonical smoke-test fixture for `lit_review_validate.py`) |

---

## Output Language

English. Academic terminology in English. Socratic mode uses natural conversational style.

---

## Quality Standards

1. **Every claim must have a citation**
2. **Evidence hierarchy**: formal proofs + empirical validation > comprehensive ablations > multi-method benchmarks > single-benchmark studies > simulation-only > expert opinion
3. **Method selection must be justified** — cite specific problem characteristics (data regime, evaluation cost, uncertainty requirements)
4. **Assumptions must be traced to limitations**
5. **Sim-to-real status must be documented** for every paper
6. **Literature organized by source field** — papers sharing a method family and field of origin go together
7. **Reproducibility** — search strategies and inclusion criteria documented for replication
8. **Socratic integrity** — in socratic mode, never give direct answers; always guide through questions
9. **Engineering framing** — output language centers on "apply/improve methods from other fields"; not algorithm invention

## Cross-Agent Quality Alignment

| Concept | Definition | Applies To |
|---------|-----------|------------|
| **Peer-reviewed** | Published in a journal with formal peer review. NeurIPS/ICML/ICRA = yes; workshops = varies; arXiv = unreviewed Tier 2 | bibliography_agent, source_verification_agent |
| **Currency Rule** | ML/deep learning = 3 years; BO/GP = 5 years; FEM/CFD/structural = 10 years. Seminal works exempt | bibliography_agent |
| **CRITICAL severity** | Issue that, if unresolved, would invalidate a core conclusion | All agents |
| **Source Tier** | Tier 1 = NeurIPS/ICML/ICRA/ASME/AIAA top journals; Tier 2 = other peer-reviewed; Tier 3 = arXiv preprints | bibliography_agent, source_verification_agent |
| **Minimum Source Count** | lit-review = 15+ | bibliography_agent |
| **Verification Threshold** | 100% DOI/arXiv check + 50% WebSearch spot-check | source_verification_agent |
| **Comparative claim** | Any paper benchmarking 2+ methods — triggers ml_comparison_bias_agent | ml_comparison_bias_agent |

> **Internal data contracts**: See `references/handoff_schemas.md` for inter-stage data exchange formats.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 4.0-engineering-application | 2026-04-24 | **Major restructure.** Deleted `academic-paper`, `academic-paper-reviewer`, `academic-pipeline` skills. Collapsed deep-research to 2 modes: `socratic` (intake → Research Frame) and `lit-review` (full pipeline + engineering-framed output). Added per-paper summary blocks (assumptions / outputs / gaps / cross-field transfer potential) and Research Agenda (exactly 3 ranked cross-field application directions with qualitative labels). Added `md_to_pdf.py` and `lit_review_validate.py` (automatic post-emission validator). Collapsed `shared/` into `deep-research/references/`. Engineering framing throughout: output centers on "apply/improve methods from other fields." No auto-invoke from Socratic to lit-review. |
| 3.2 | 2026-04-22 | Full-text retrieval & vault-shaped output. Added `paper_fetch_agent`. Report compiler adds `synthesize` and `paper-review` vault modes. `deep-research-agents-used:` envelope marker. Bundled scripts. |
| 3.1 | 2026-04-05 | Collapsed to 4 phases. Added `ml_comparison_bias_agent`. Research Scope Protocol replaces FINER/PICOS. Plain markdown with numbered references. |
| 2.4 | 2026-03-27 | Style Profile consumption and Writing Quality Check in report compiler. |
| 2.3 | 2026-03-08 | Added `monitoring_agent`. Enhanced socratic_mentor with convergence signals. |
| 2.0 | 2026-02 | Socratic mode (10th agent), failure paths, mode selection guide, handoff protocol |
| 1.0 | 2026-02 | Initial release |
