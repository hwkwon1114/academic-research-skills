# Quick Start

Get from zero to your first lit-review in 3 steps.

## Step 1: Install

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
mkdir -p ~/.claude/skills
ln -s ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
```

Optional — install pandoc for PDF output:
```bash
brew install pandoc   # macOS
# apt install pandoc  # Linux
```

## Step 2: Launch

```bash
claude
```

## Step 3: Start

### Option A — Socratic mode (if your frame is unclear)

```
You: "Guide my research: I want to apply ML to aerospace structural optimization
      but I'm not sure which method family fits my data regime."
```

Socratic asks ≥3 narrowing questions (engineering domain → method family → open problem), then emits a **Research Frame** block and this prompt:

> "Your Research Frame is ready. Next step: run lit-review with this Frame — paste this block into a new prompt or type 'run lit-review'."

Then:

```
You: "run lit-review"
```

### Option B — Lit-review mode (if you already have a Research Frame)

```
You: "Run lit-review. Here is my Research Frame:
- engineering_domain: topology optimization for aerospace structures
- method_family_of_interest: Bayesian optimization
- open_problem: discrete design variables break GP surrogate assumptions
- ..."
```

## What you get

- Per-paper summary blocks (assumptions / outputs / gaps / cross-field transfer potential)
- Research Agenda: exactly 3 ranked directions, each framed as:
  `Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]`
- Markdown report + PDF saved to `reports/`

## Mode reference

| I want to... | Use this |
|-------------|----------|
| Clarify my research frame | `socratic` mode — describe your engineering problem |
| Run a literature review | `lit-review` mode — provide or paste a Research Frame |

Socratic does **not** auto-invoke lit-review. You control when to run it.
