# Mode Selection Guide

## Overview

`deep-research` has two modes:

1. **`socratic`** — intake mode. Narrows the research frame through guided dialogue. Produces a Research Frame artifact and a user-confirmation handoff prompt. **No auto-chain to lit-review.**
2. **`lit-review`** — output mode. Runs the full literature pipeline and produces an engineering-framed report with per-paper summary blocks and a 3-direction Research Agenda.

---

## Decision Flow

```text
User Input
 |
 +-- Already have a converged Research Frame? --> lit-review
 +-- Unclear frame, want guided thinking?    --> socratic
                                                  (emits Research Frame + user-confirmation prompt)
                                                  (user must explicitly invoke lit-review)
```

**No auto-invoke from Socratic to lit-review.** Socratic always ends by printing:
> "Your Research Frame is ready. Next step: run lit-review with this Frame — paste this block into a new prompt or type 'run lit-review'."

**Socratic is a prerequisite for lit-review** unless the user already has a Research Frame (from a prior Socratic session or written by hand matching `references/research_frame_schema.md`).

---

## Mode Guide

### `socratic`

**Use when**
- The user is unsure which engineering domain, method family, or open problem to focus on
- The research frame is unclear or underspecified
- The user wants guided thinking before committing to a literature search

**Best fit examples**
- "Guide my research: I want to apply ML to structural optimization but I'm not sure which method fits."
- "Help me think through whether representation or data cost is the real bottleneck."
- "I want to use Bayesian optimization for aerodynamic design but I'm not sure what the open problem is."

**What it produces**
- A converged Research Frame (10 fields: engineering domain, method family, open problem, baseline approach, data regime, scope notes, failure modes, scope boundaries, origin layer, validation status)
- A user-confirmation handoff prompt

**What it does NOT produce**
- A literature report
- A paper outline
- Auto-invocation of lit-review

---

### `lit-review`

**Use when**
- The user has a converged Research Frame (from Socratic or written directly)
- The main deliverable is a literature synthesis + Research Agenda

**Best fit examples**
- "Run lit-review. Here is my Research Frame: [block]"
- "Literature review on applying Bayesian optimization to discrete topology optimization."
- "Review the literature on cross-field transfer of physics-informed neural networks to structural health monitoring."

**What it produces**
1. Per-paper summary blocks (Assumptions / Outputs / Gaps / Cross-Field Transfer Potential) for every key paper
2. Assumption Map, Sim-to-Real Summary, Representation Audit, Gap Analysis (annotated with `failure_modes[]` from the Research Frame)
3. Research Agenda — exactly 3 ranked cross-field application directions (`highest tractable` / `medium` / `stretch-exploratory`), each matching: `Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]`
4. Markdown report + PDF (if pandoc available), saved to `reports/<slug>-<date>.md` and `.pdf`

**Routing behavior within lit-review**
- Physics-heavy frame: bibliography queries start with physics process, data modality, fidelity, representation
- Method-first frame: preserve direct family comparison in the synthesis
- Cross-field frame: organize bibliography by source field (not by engineering domain)

---

## Regression Protection Cases

### Case 1 — Socratic (unclear frame)
**Prompt:** "Guide my research: I want to apply ML for design optimization but I'm not sure where to start."
**Expected:** Socratic fires Layer 1 (engineering domain narrowing), Layer 2 (method family + source field), Layer 3 (open problem). Emits Research Frame. Prints handoff prompt. No auto-invoke of lit-review.

### Case 2 — Lit-review (frame already provided)
**Prompt:** "Run lit-review. Frame: topology optimization / Bayesian optimization / discrete variable handling."
**Expected:** lit-review pipeline fires directly. Produces per-paper blocks + Research Agenda. No Socratic intake.

### Case 3 — Socratic → Lit-review transition
**Prompt (turn 1):** "Guide my research on applying reinforcement learning to thermal management."
**Expected (turn 1):** Socratic fires. Narrows frame across Layers 1-3.
**Expected (convergence):** Research Frame emitted. User-confirmation handoff prompt printed.
**Prompt (turn 2):** "run lit-review"
**Expected (turn 2):** lit-review fires using the Research Frame from the prior Socratic session.

---

## Transition Notes

Only one valid transition exists:

```text
socratic → lit-review  (user-initiated, not auto-chained)
```

The user must explicitly invoke lit-review after reviewing and accepting the Research Frame. This makes the transition auditable and prevents the literature search from running on an underspecified frame.
