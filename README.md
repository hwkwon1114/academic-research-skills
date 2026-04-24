# deep-research — Engineering Lit-Review and Cross-Field Research Direction

[![Version](https://img.shields.io/badge/version-v4.0-blue)](https://github.com/Imbad0202/academic-research-skills)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)

## What this does

A single Claude Code skill for engineering researchers who want to find where methods from other fields can be applied or improved in their domain. Not to write papers — to find the right research direction.

Two modes:

- **`socratic`** — guided dialogue that narrows your research frame (engineering domain, method family, open problem). Produces a Research Frame artifact. No auto-chain.
- **`lit-review`** — full literature pipeline. Takes a Research Frame, produces per-paper summary blocks (assumptions / outputs / gaps / cross-field transfer potential) and a Research Agenda with exactly 3 ranked cross-field application directions.

Output: `Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]`.

## Quick Start

```bash
# Install
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
mkdir -p ~/.claude/skills
ln -s ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
```

Then in Claude Code:

```
# Step 1 — narrow your frame (if unclear)
Guide my research: I want to apply ML to topology optimization but I'm not
sure which method family fits my data regime.

# Step 2 — run the literature review (after Socratic emits your Research Frame)
run lit-review
```

Socratic emits a Research Frame block and a handoff prompt. You paste or type "run lit-review" to trigger the literature pipeline. **No auto-invoke.**

## What lit-review produces

- **Per-paper summary blocks** — for every key paper: assumptions, outputs/contributions, gaps/limitations, cross-field transfer potential
- **Research Agenda** — exactly 3 ranked directions (`highest tractable` / `medium` / `stretch-exploratory`), each framed as: `Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain]`
- Markdown + PDF saved to `reports/<slug>-<date>.md` and `.pdf` (PDF requires `brew install pandoc`)

## PDF output

```bash
brew install pandoc   # one-time setup
```

If pandoc is not installed, the report saves as Markdown with a clear install-message. The validator accepts this gracefully.

## Installation

Symlink into `~/.claude/skills/` for global access:

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
mkdir -p ~/.claude/skills
ln -s ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
```

To update: `git pull` inside the repo — no re-linking needed.

For project-scoped install, symlink into `.claude/skills/` relative to the project root.

## Skills

| Skill | Version | Purpose |
|-------|---------|---------|
| `deep-research` | v4.0 | Engineering lit-review + cross-field Research Agenda |

## License

CC-BY-NC 4.0 — free for non-commercial research use.
