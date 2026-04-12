# Mode Selection Guide

## Overview

`deep-research` still exposes the same user-facing modes, but mode selection now happens **after** a routing pre-check:

1. **Physics-heavy**
2. **Representation-sensitive**
3. **Method-first**
4. **Generic / non-physics**

The routing class determines the **intake order**, not the whole pipeline. The stable downstream backbone remains **model-family / assumption-lineage synthesis**.

---

## Routing Pre-Check

Classify the prompt before choosing a mode.

| Prompt class | Trigger signals | First intake focus | Must avoid |
|---|---|---|---|
| **Physics-heavy** | PDEs, operator learning, CFD/FEM solvers, expensive simulations or experiments, multi-fidelity, sim-to-real | Physics system -> data source/acquisition path -> fidelity ladder -> representation -> evaluation/sim-to-real constraints | Jumping straight to architecture ranking |
| **Representation-sensitive** | Meshes, fields, graphs, topology change, operators, latent spaces, encoding bottlenecks | What must be represented, which encodings are plausible, whether representation is the bottleneck | Treating representation as a late-stage detail |
| **Method-first** | “compare X vs Y”, benchmark request, architecture ranking | Immediate method-family comparison, with only lightweight context if helpful | Forcing solver/fidelity intake before any comparison |
| **Generic / non-physics** | Broad research question without physics/data/representation signals | Standard broad research intake | Injecting irrelevant physics-specific questions |

**Override rule:** explicit method-comparison requests override physics-heavy defaults unless the user asks for broader scoping.

---

## Decision Flow

```text
User Input
 |
 +-- Have text to review? ------------------------> review
 +-- Only need fact verification? ----------------> fact-check
 +-- Need guided thinking / no clear question? --> socratic
 +-- Explicit method comparison? -----------------> quick or lit-review
 +-- Need complete research output? -------------> full
 +-- Need literature-focused output only? -------> lit-review
 +-- Otherwise ----------------------------------> quick
```

Use the routing pre-check to shape intake **inside** the selected mode:
- `full` and `socratic` use the most routing-sensitive intake
- `lit-review` uses routing to shape the bibliography and synthesis order
- `quick` uses routing to decide whether to lead with physics/data/representation or direct method comparison

---

## Mode Guide

### `full`

**Use when**
- The user needs complete scoping, investigation, synthesis, and a final report
- The topic is physics-heavy and needs careful acquisition/fidelity/representation framing

**Best fit examples**
- “I need literature on PDE/operator learning for fast data-efficient physics-model surrogates.”
- “Research multi-fidelity strategies for combustion-model surrogates.”

**Routing behavior**
- Physics-heavy prompts: full front-end intake
- Representation-sensitive prompts: representation-first intake
- Method-first prompts: comparison first, then scoped expansion if needed

---

### `quick`

**Use when**
- The user needs a fast brief or first-pass orientation
- The user explicitly asks for a concise comparison or overview

**Best fit examples**
- “Quick brief on graph vs field representations for surrogate modeling.”
- “Compare PINNs and FNOs for PDE surrogates.”

**Routing behavior**
- Method-first prompts often belong here
- Physics-heavy prompts can still use quick mode, but the brief should mention data source, fidelity, and representation before ranking methods

---

### `lit-review`

**Use when**
- The user needs literature search + synthesis, but not a full report
- The main deliverable is an annotated bibliography plus structured synthesis

**Best fit examples**
- “Literature review on multi-fidelity operator learning.”
- “Review the literature on topology-aware representations for structural surrogates.”

**Routing behavior**
- Physics-heavy: bibliography queries start with physics process, data modality, fidelity, and representation
- Method-first: preserve direct family comparison in the synthesis

---

### `fact-check`

**Use when**
- The user wants specific claims, citations, or references checked

**Best fit examples**
- “Verify whether this PDE surrogate paper has a peer-reviewed version.”
- “Fact-check this claim about hardware validation in operator learning.”

**Routing behavior**
- Do not escalate into full physics-first intake unless the user expands scope

---

### `review`

**Use when**
- The user already has a draft, report, or manuscript and wants critique

**Best fit examples**
- “Review this surrogate-modeling survey.”
- “Check whether this draft overclaims from simulation-only evidence.”

**Routing behavior**
- Apply the routing class to critique emphasis:
  - physics-heavy -> overclaiming from solver-only evidence
  - representation-sensitive -> whether encoding risks are ignored
  - method-first -> whether comparisons are fair and scoped

---

### `socratic`

**Use when**
- The user is unsure how to frame the research problem
- The main need is guided thinking, not immediate report generation

**Best fit examples**
- “Help me think through whether representation or data cost is the real bottleneck.”
- “Guide my research on physics-based surrogates.”

**Routing behavior**
- Physics-heavy: ask physics/data/fidelity/representation first
- Representation-sensitive: stay on encoding sufficiency before method choice
- Method-first: comparison can be discussed, but only if the user wants exploration rather than direct output

---

## Regression Protection Cases

### Case 1 — Physics-heavy
**Prompt:** “I need literature on PDE/operator learning for fast data-efficient physics-model surrogates.”
**Expected:** asks about solver cost, fidelity ladder, representation, and validation scope before model ranking.

### Case 2 — Representation-sensitive
**Prompt:** “Help me study which representation works best for topology-changing physics surrogates.”
**Expected:** asks what must be represented and whether representation is the bottleneck before method ranking.

### Case 3 — Method-first
**Prompt:** “Compare DeepONet, FNO, and PINNs for PDE surrogate learning.”
**Expected:** direct method-family comparison path is preserved immediately.

### Case 4 — Generic / non-physics
**Prompt:** broad non-physics literature request.
**Expected:** no unnecessary solver/fidelity intake.

---

## Transition Notes

Common safe transitions:

```text
socratic -> full
socratic -> lit-review
quick -> full
quick -> lit-review
lit-review -> full
fact-check -> full
```

Routing class should be preserved across transitions unless the user changes the task.

Example:
- A `quick` method-first comparison can transition into `full`, but once the user broadens scope, the intake may expand into physics/data/fidelity/representation framing.

---

## Handoff Reminder

Mode selection decides **how the work starts**. It does **not** replace the backend:
- bibliography still hands off into model families
- synthesis still preserves assumption lineage
- source verification still grades evidence quality separately from novelty/currentness
