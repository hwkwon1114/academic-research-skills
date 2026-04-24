# Changelog

All notable changes to this project will be documented in this file.

## [4.0] - 2026-04-24 — Engineering Lit-Review + Cross-Field Agenda

### Removed
- `academic-paper` skill (v2.5) — deleted entirely
- `academic-paper-reviewer` skill (v1.4) — deleted entirely
- `academic-pipeline` skill (v2.7) — deleted entirely
- `examples/showcase/` — deleted (contained only academic pipeline artifacts)
- `shared/` directory — collapsed into `deep-research/references/`

### Changed
- `deep-research` is now the only skill in this repo
- Collapsed `deep-research` to 2 modes: `socratic` (intake → Research Frame) and `lit-review` (full pipeline)
- Removed modes: `full`, `quick`, `review`, `fact-check`, `synthesize`, `paper-review`
- `socratic` mode now produces a Research Frame (10-field schema) instead of a Research Plan Summary
- No auto-invoke from Socratic to lit-review — explicit user confirmation required

### Added
- Per-paper summary blocks in lit-review output: Assumptions / Outputs / Gaps / Cross-Field Transfer Potential
- Research Agenda section: exactly 3 ranked cross-field application directions with qualitative labels (`highest tractable` / `medium` / `stretch-exploratory`)
- Apply/improve template: `Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]`
- `scripts/md_to_pdf.py` — pandoc-based PDF conversion with loud fallback warning
- `scripts/lit_review_validate.py` — automatic post-emission validator (6 checks; blocks agent completion on failure)
- `deep-research/references/research_frame_schema.md` — standalone Research Frame schema (10 fields)
- `deep-research/references/handoff_schemas.md` — internal data contracts (moved + rewritten from `shared/`)
- `deep-research/references/cross_model_verification.md` — optional cross-model verification (moved from `shared/`)
- `deep-research/examples/lit_review_with_agenda.md` — canonical smoke-test fixture for the validator
- Git rollback tag `pre-redesign-v3.2` created before deletion

### Engineering framing
- All output language centers on "apply/improve methods from other fields" — not algorithm invention
- Gap Analysis annotates `failure_modes[]` from Research Frame against retrieved papers
- Direction 3 (stretch-exploratory) respects `scope_boundaries[]` from Research Frame
- References use numbered format `[1] Author, Year. Title. Venue.` (not APA narrative)

---

## [3.2] - 2026-04-22

Full-text retrieval & vault-shaped output. Added `paper_fetch_agent`. Report compiler adds `synthesize` and `paper-review` vault modes. `deep-research-agents-used:` envelope marker. Bundled scripts.

## [3.1] - 2026-04-05

Collapsed to 4 phases. Added `ml_comparison_bias_agent`. Research Scope Protocol replaces FINER/PICOS. Plain markdown with numbered references.

## [2.9.1] - 2026-04-03

`status` and `related_skills` metadata added to all 4 SKILL.md frontmatters.

## [2.9] - 2026-03-27

Style Calibration + Writing Quality Check. Information Systems Basket of 8 journals.

## [2.8] - 2026-03-22

SCR Loop Phase 1 — State-Challenge-Reflect mechanism in Socratic Mentor Agent.

## [2.7] - 2026-03-09

Full academic research skills suite (4 skills, 116 files). Integrity Verification v2.0.
