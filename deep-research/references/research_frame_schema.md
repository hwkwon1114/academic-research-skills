# Research Frame Schema

Standalone reference for the Research Frame artifact produced by `socratic_mentor_agent` and consumed by `report_compiler_agent`.

Full schema definition is in `deep-research/references/handoff_schemas.md` (Schema 4). This file provides a quick-reference for agents.

---

## Fields (all 10 required)

| Field | Type | Description |
|-------|------|-------------|
| `engineering_domain` | string | The engineering field being investigated (e.g., aerospace structures, thermal management, biomechanics) |
| `method_family_of_interest` | string | The ML/computational method family under consideration (e.g., Bayesian optimization, physics-informed neural networks, Gaussian processes) |
| `open_problem` | string | The specific unsolved problem or performance gap in the engineering domain |
| `baseline_approach` | string | The current best method used in this domain for this problem |
| `data_regime` | string | Data availability and quality context (e.g., sparse experimental, high-fidelity simulation, multi-fidelity) |
| `scope_notes` | list[string] | Any additional scoping constraints or clarifications |
| `failure_modes` | list[string] | Known failure modes or breakdown conditions of the baseline approach; consumed by Gap Analysis in report |
| `scope_boundaries` | list[string] | Explicitly declared out-of-scope items; consumed to narrow the `stretch-exploratory` Research Agenda direction |
| `origin_layer` | int (1–5) | Socratic layer at which frame converged |
| `validation_status` | enum | `frame-converged` / `frame-partial` |

## Validation

- `validation_status` must be `frame-converged` before handoff.
- `failure_modes` and `scope_boundaries` may be empty lists `[]` but must be present.
- Missing any field → `HANDOFF_INCOMPLETE`.

## Emitted Format

Socratic emits the Research Frame as a fenced Markdown block, then prints the user-confirmation handoff prompt:

```markdown
## Research Frame

- **engineering_domain**: [value]
- **method_family_of_interest**: [value]
- **open_problem**: [value]
- **baseline_approach**: [value]
- **data_regime**: [value]
- **scope_notes**: [list]
- **failure_modes**: [list]
- **scope_boundaries**: [list]
- **origin_layer**: [int]
- **validation_status**: frame-converged
```

> "Your Research Frame is ready. Next step: run lit-review with this Frame — paste this block into a new prompt or type 'run lit-review'."

## Consumer Wiring

`report_compiler_agent` consumes this Frame as follows:
- **Section 3 (Research Frame)**: echo all 10 fields verbatim.
- **Section 9 (Gap Analysis)**: annotate each `failure_modes[]` item — which retrieved papers address it? Unaddressed items are explicit gaps.
- **Section 10 (Research Agenda, Direction 3 — stretch-exploratory)**: the direction MUST respect `scope_boundaries[]`. It may push past current scope but must not violate any explicitly-declared out-of-scope item.
