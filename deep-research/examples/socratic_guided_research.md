# Socratic Mode Example: ML for Structural Optimization

This example demonstrates the Socratic mode flow: multi-round dialogue narrows the engineering domain, method family, and open problem → converged Research Frame → user-confirmation handoff prompt. No auto-invoke of lit-review.

---

## Scenario Setup

**User**:
```
Guide my research: I want to apply ML to structural optimization but I'm not sure
which method family fits my data regime or what the real performance gap is.
```

**System**: Detects "guide my research" + unclear frame → activates Socratic mode → invokes `socratic_mentor_agent`.

---

## Layer 1: PROBLEM CHARACTERIZATION

### Round 1

**Socratic Mentor**:

Structural optimization is a broad space — it spans topology, shape, sizing, and multi-physics problems, each with very different data regimes. Before we talk methods, let me understand the engineering context.

What is the specific design task you're working on? For example: topology optimization of a load-bearing aerospace component, sizing optimization of a truss structure, shape optimization of a heat sink? And what does each design evaluation cost — is this a quick finite element run (seconds) or a high-fidelity simulation (hours)?

**User**:
I'm working on topology optimization for aerospace structural parts. The FEM runs are pretty expensive — around 30 minutes each on our cluster. We have a budget of maybe 300–500 evaluations total.

**Socratic Mentor**:

That's a very clear engineering context — thank you. A 30-minute FEM with a 300–500 evaluation budget immediately tells us something important: you're in the expensive-evaluation regime where data-efficient methods matter most.

One more thing before we move to methods: what does success look like in engineering terms? Not "the model has low RMSE" — but what does a better topology actually give you? Reduced structural mass, improved compliance, fewer stress concentrations?

**User**:
Minimizing structural compliance (maximizing stiffness) at a given volume fraction. The standard SIMP method works okay for continuous variable relaxations but breaks down when we need discrete solutions — actual binary inclusion/exclusion of elements.

**Socratic Mentor**:

Excellent — you've just named the engineering domain precisely. Topology optimization for aerospace structural compliance minimization, with a discrete design variable problem that SIMP's continuous relaxation cannot handle cleanly. That's a well-defined problem with a clear performance gap.

[DA checkpoint: Problem framing implies a clear data regime (sparse, expensive FEM) and engineering success criterion (compliance minimization). The discrete variable constraint is a genuine assumption violation for standard surrogate methods. Layer 1 complete.]

---

## Layer 2: METHOD-ASSUMPTION FIT

### Round 2

**Socratic Mentor**:

Now let's talk methods. You mentioned SIMP breaks down on discrete variables. What ML or optimization method are you considering as an alternative? And what assumption does that method make that might or might not fit your binary element space?

**User**:
I was thinking Bayesian optimization with Gaussian process surrogates. Everyone uses it for expensive black-box optimization.

**Socratic Mentor**:

That's a reasonable starting point — BO with GPs is the go-to for expensive evaluation budgets. But here's the question I want you to sit with: what assumption does a GP make about the response landscape?

**User**:
It assumes the function is smooth and continuous — correlated nearby points behave similarly.

**Socratic Mentor**:

Exactly. And now apply that to your problem: when you flip a single binary element from 0 to 1 in a topology, does the compliance change smoothly, or can it jump discontinuously?

**User**:
It can jump — especially if that element is on a load path. Flipping one element can completely change the structural flow.

**Socratic Mentor**:

Right. So you've identified the core assumption mismatch: GP surrogates assume smooth continuous landscapes, but binary topology creates combinatorial jumps. That's the method-assumption fit problem you need to solve.

Now — here's the cross-field question. Which field outside aerospace structures already handles discrete or combinatorial optimization with surrogate models? Where has someone solved a similar "binary space + expensive evaluation" problem?

**User**:
Drug discovery? They optimize molecular structures which are also discrete.

**Socratic Mentor**:

Exactly. Drug discovery has 10+ years of BO-over-discrete-graphs literature. The COMBO method uses graph diffusion kernels over combinatorial molecular spaces — directly analogous to binary topology layouts. What does that suggest about where to look for methods?

[DA checkpoint: Method-assumption fit is correctly identified. GP smoothness violated by discrete topology. Source field named: drug discovery / combinatorial optimization. Layer 2 complete.]

---

## Layer 3: VALIDATION DESIGN

### Round 3

**Socratic Mentor**:

Let's crystallize the open problem. You have GP surrogates that assume smoothness, but binary topology violates that assumption. What exactly fails — is it that BO converges to the wrong topology, or that it's just slower than SIMP?

**User**:
Mainly that it converges to the wrong topology — the acquisition function explores the wrong regions of the binary space because the GP is inaccurate over discontinuous jumps.

**Socratic Mentor**:

That's the open problem stated precisely: discrete design variables break GP surrogate accuracy in topology optimization, causing BO to explore suboptimally relative to gradient-based SIMP methods.

Last question for this layer: will your validation be simulation-only, or do you need hardware-validated structural testing?

**User**:
Simulation-only for now — we'd validate against SIMP on benchmark topology problems like the MBB beam.

[Layer 3 complete. All three core frame fields are now converged. Compiling Research Frame.]

---

## Convergence — Research Frame

All convergence signals active: S1 (open problem stated clearly), S2 (assumption mismatch identified), S3 (method family justified against alternatives), S4 (scope stable for 3 rounds).

```markdown
## Research Frame

- **engineering_domain**: Topology optimization for aerospace structural components (compliance minimization)
- **method_family_of_interest**: Bayesian optimization with non-GP surrogates (graph kernels, discrete-space BO)
- **open_problem**: Discrete binary design variables violate GP smoothness assumptions, causing BO acquisition to explore suboptimally in binary topology spaces
- **baseline_approach**: SIMP (Solid Isotropic Material with Penalization) with sensitivity-based gradient descent
- **data_regime**: High-fidelity FEM (~30 min/evaluation); budget 300–500 evaluations; simulation-only
- **scope_notes**: 2D and 3D structural compliance minimization; fixed load/boundary conditions; single-material
- **failure_modes**: ["GP surrogate assumes smooth continuous landscape — binary variables create combinatorial jumps", "Acquisition function optimization becomes NP-hard over binary domains"]
- **scope_boundaries**: ["No multi-material optimization", "No hardware structural testing in scope", "No fluid topology (e.g. flow channels)"]
- **origin_layer**: 3
- **validation_status**: frame-converged
```

> "Your Research Frame is ready. Next step: run lit-review with this Frame — paste this block into a new prompt or type 'run lit-review'."

---

## User invokes lit-review

```
run lit-review
```

**System**: lit-review mode fires using the Research Frame above. Produces per-paper summary blocks + Research Agenda. See `examples/lit_review_with_agenda.md` for the full output.
