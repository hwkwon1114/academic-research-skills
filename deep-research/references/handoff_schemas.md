# Handoff Schemas — deep-research Internal Data Contracts

## Purpose

Defines the exact data structure for every artifact passed between deep-research pipeline stages.
All agents that produce or consume these artifacts MUST conform to these schemas.
Consuming agents should validate input and request re-generation if schema violations are found.

> **Convention**: All schemas use Markdown-based structured output. Agents MUST validate required fields before accepting a handoff. Missing required fields trigger a `HANDOFF_INCOMPLETE` failure path.

---

## Schema 1: RQ Brief (research_question_agent / socratic_mentor_agent → research_architect_agent)

**Producer**: `research_question_agent` | `socratic_mentor_agent`
**Consumer**: `research_architect_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `research_question` | string | The finalized research question (single sentence, interrogative form) |
| `sub_questions` | list[string] | 2-5 decomposed sub-questions |
| `finer_scores` | object | `{feasible: 1-10, interesting: 1-10, novel: 1-10, ethical: 1-10, relevant: 1-10}` |
| `scope` | object | `{in_scope: list[string], out_of_scope: list[string], domain: string, timeframe: string}` |
| `methodology_type` | enum | `"qualitative"` / `"quantitative"` / `"mixed"` |
| `keywords` | list[string] | 5-10 search terms for literature search |

### Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `socratic_insights` | list[string] | Key insights from Socratic dialogue (if socratic mode) |
| `hypothesis` | string | Preliminary hypothesis (if applicable) |
| `exclusion_criteria` | list[string] | What is explicitly out of scope |

---

## Schema 2: Bibliography (bibliography_agent → synthesis_agent / source_verification_agent)

**Producer**: `bibliography_agent`
**Consumer**: `synthesis_agent` | `source_verification_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `sources` | list[Source] | All identified sources (minimum 15 for lit-review mode, 5 for quick) |
| `search_strategy` | object | `{databases: list[string], keywords: list[string], inclusion_criteria: list[string], exclusion_criteria: list[string], date_range: string}` |
| `coverage_assessment` | string | Self-assessment of literature coverage completeness |
| `minimum_sources` | integer | 15 (lit-review mode) |

### Source Object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (e.g., `[S01]`) |
| `title` | string | Yes | Source title |
| `authors` | string | Yes | Author(s) |
| `year` | integer | Yes | Publication year |
| `doi` | string | Yes* | DOI if available (*required for journal articles) |
| `citation` | string | Yes | Full citation in numbered format `[N] Author, Year. Title. Venue.` |
| `type` | enum | Yes | `journal_article` / `book` / `chapter` / `conference` / `report` / `preprint` |
| `evidence_tier` | integer | Yes | 1-7 (1 = systematic review/meta-analysis, 7 = expert opinion) |
| `relevance` | enum | Yes | `core` / `supporting` / `peripheral` |
| `relevance_score` | integer | Yes | 1-10 relevance to the research question |
| `annotation` | string | Yes | 2-3 sentence summary of key findings and relevance |

---

## Schema 3: Synthesis Report (synthesis_agent → report_compiler_agent)

**Producer**: `synthesis_agent`
**Consumer**: `report_compiler_agent`

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `themes` | list[Theme] | 3-7 synthesized themes (NOT per-source summaries) |
| `research_gaps` | list[string] | What the literature does NOT address |
| `key_debates` | list[Debate] | Where sources disagree, with analysis |
| `consensus_areas` | list[string] | Where sources agree |

### Theme Object

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Theme label |
| `description` | string | 3-5 sentence synthesis across multiple sources |
| `supporting_sources` | list[string] | Source IDs that contribute to this theme |
| `strength` | enum | `strong` (5+ sources) / `moderate` (3-4) / `emerging` (1-2) |

### Debate Object

| Field | Type | Description |
|-------|------|-------------|
| `position_a` | string | First position |
| `position_b` | string | Opposing position |
| `sources_a` | list[string] | Source IDs supporting position A |
| `sources_b` | list[string] | Source IDs supporting position B |
| `evidence_balance` | string | Analysis of which position has stronger evidence and why |

---

## Schema 4: Research Frame (socratic_mentor_agent → report_compiler_agent / user)

**Producer**: `socratic_mentor_agent` (on convergence)
**Consumer**: `report_compiler_agent` | user (for lit-review invocation)

This schema is also maintained as a standalone file at `deep-research/references/research_frame_schema.md` for direct agent referencing.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `engineering_domain` | string | The engineering field being investigated (e.g., aerospace structures, thermal management, biomechanics) |
| `method_family_of_interest` | string | The ML/computational method family under consideration (e.g., Bayesian optimization, physics-informed neural networks, Gaussian processes) |
| `open_problem` | string | The specific unsolved problem or performance gap in the engineering domain |
| `baseline_approach` | string | The current best method used in this domain for this problem |
| `data_regime` | string | Data availability and quality context (e.g., sparse experimental, high-fidelity simulation, multi-fidelity) |
| `scope_notes` | list[string] | Any additional scoping constraints or clarifications |
| `failure_modes` | list[string] | Known failure modes or breakdown conditions of the baseline approach in this domain |
| `scope_boundaries` | list[string] | Explicitly declared out-of-scope items; used to narrow the stretch-exploratory direction in the Research Agenda |
| `origin_layer` | int | Socratic layer at which frame converged (1–5) |
| `validation_status` | enum | `frame-converged` (all three core fields confirmed) / `frame-partial` (converged on 1-2 fields only) |

### Validation Rules

- `validation_status` must be `frame-converged` before report_compiler_agent accepts the Frame.
- All 10 fields must be present; missing fields trigger `HANDOFF_INCOMPLETE`.
- `failure_modes` and `scope_boundaries` may be empty lists `[]` but must be present.

### Emitted Format

The Research Frame is emitted as a fenced Markdown block:

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

---

## Validation Rules (all schemas)

1. **Required field check**: All fields without "(optional)" designation are REQUIRED.
2. **Type check**: Fields must match declared types.
3. **Failure on missing**: If a required field is missing, return `HANDOFF_INCOMPLETE` with a list of missing fields; do NOT proceed with partial data.
4. **Producer validation**: Producing agent must validate output against its schema BEFORE handoff.
5. **Consumer validation**: Consuming agent should validate input on receipt and request re-generation if schema violations are found.
