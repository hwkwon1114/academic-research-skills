# CLAUDE.md

This file provides guidance to Claude Code when working with code in this repository.

## What This Repo Is

A single Claude Code skill (`deep-research`) for engineering literature review and cross-field research direction synthesis. Skills are installed by users into their own projects via `git clone` — this repo has no build system or test runner.

## Skill File Structure

```
deep-research/
├── SKILL.md          # Required: YAML frontmatter + instructions
├── agents/           # Sub-agent instruction files (.md)
├── references/       # Reference docs and schemas
├── scripts/          # Python scripts called by agents
├── templates/        # Output templates
└── examples/         # Example outputs
```

The `description` field in SKILL.md frontmatter is the primary trigger mechanism.

## Routing Rules

- Use `deep-research socratic` when the research frame is unclear (engineering domain, method family, or open problem not yet specified).
- Use `deep-research lit-review` when the frame is set (Research Frame artifact available).
- Socratic does **not** auto-chain to lit-review — the user must explicitly invoke lit-review after reviewing the Research Frame.

## Key Contracts

- `deep-research/references/research_frame_schema.md` — the 10-field Research Frame schema that Socratic produces and lit-review consumes.
- `deep-research/references/handoff_schemas.md` — all internal data contracts (Schemas 1–4).
- `deep-research/scripts/lit_review_validate.py` — invoked automatically by `report_compiler_agent` post-emission; blocks completion on failure.
- `deep-research/scripts/md_to_pdf.py` — converts Markdown report to PDF; requires pandoc.

## Versioning Convention

`SKILL.md` has `metadata.version` and `metadata.last_updated`. Bump version and date when making substantive changes to agent behavior, trigger conditions, or output schemas.

## Language Policy

All user-facing output defaults to English. Technical terms remain in English.

## Installation (for users)

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
mkdir -p ~/.claude/skills
ln -s ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
```

Symlinks mean edits to the repo are reflected immediately. To update: `git pull` inside the repo.
