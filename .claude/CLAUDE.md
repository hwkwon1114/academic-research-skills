# Academic Research Skills

A single Claude Code skill for rigorous engineering literature review and cross-field research direction synthesis.

## Skills Overview

| Skill | Version | Purpose | Modes |
|-------|---------|---------|-------|
| `deep-research` | v4.0 | Engineering lit-review + cross-field Research Agenda | `socratic`, `lit-review` |

## Routing Rules

1. **socratic vs lit-review**: Use `socratic` when the research frame is unclear. Use `lit-review` when the frame is set. Socratic does **not** auto-chain — the user must explicitly invoke lit-review after reviewing the Research Frame.

2. **Research Frame**: Socratic produces a 10-field Research Frame (engineering domain, method family, open problem, baseline approach, data regime, scope notes, failure modes, scope boundaries, origin layer, validation status). Lit-review requires a `frame-converged` Research Frame to run.

3. **Output contract**: Lit-review always produces per-paper summary blocks (Assumptions / Outputs / Gaps / Cross-Field Transfer Potential) and a Research Agenda with exactly 3 ranked cross-field application directions. The validator (`scripts/lit_review_validate.py`) enforces this automatically.

## Key Rules

- All claims must have `[N]` numbered citations
- Evidence hierarchy respected (formal proofs + empirical validation > ablations > benchmarks > simulation-only > expert opinion)
- Engineering framing: output centers on "apply/improve methods from other fields" — not algorithm invention
- No silent fallback from PDF to Markdown — user must see the install-message warning
- No auto-invoke from Socratic to lit-review

## Version Info
- **Version**: 4.0
- **Last Updated**: 2026-04-24
- **License**: CC-BY-NC 4.0
