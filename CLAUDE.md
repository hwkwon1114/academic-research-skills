# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

A collection of Claude Code skills for academic research and publication. Skills are installed by users into their own projects via `git clone` — this repo itself has no build system or test runner.

## Skill File Structure

Each skill follows this layout:
```
<skill-name>/
├── SKILL.md          # Required: YAML frontmatter (name, description, metadata) + instructions
├── agents/           # Sub-agent instruction files (.md)
├── references/       # Reference docs loaded into context on demand
├── templates/        # Output templates
└── examples/         # Example outputs or walkthroughs
```

The `description` field in SKILL.md frontmatter is the primary trigger mechanism — Claude decides whether to invoke a skill based on that text. Keep it dense with trigger phrases (both English and 繁體中文).

## Shared Resources

`shared/` contains cross-skill contracts used by multiple skills:
- `handoff_schemas.md` — Strict data schemas for artifacts passed between pipeline stages (RQ Brief, Methodology Blueprint, Annotated Bibliography, etc.). Agents validate input against these schemas; missing required fields trigger `HANDOFF_INCOMPLETE`.
- `style_calibration_protocol.md` — Protocol for learning an author's writing voice from past papers (used by academic-paper intake Step 10 and deep-research report compiler).
- `cross_model_verification.md` — Optional GPT/Gemini second-reviewer integration activated via `ARS_CROSS_MODEL` env var.

## Skill Routing Logic (authoritative in .claude/CLAUDE.md)

The full routing rules live in `.claude/CLAUDE.md`. Key principle: `academic-pipeline` is the full orchestrator; trigger individual skills directly when the user only needs one stage.

## Versioning Convention

Each SKILL.md has `metadata.version` and `metadata.last_updated`. Bump the version and date when making substantive changes to agent behavior, trigger conditions, or output schemas.

## Language Policy

All user-facing output defaults to the user's input language (Traditional Chinese or English). Trigger keywords in SKILL.md descriptions must cover both languages.

## Installation (for users)

Clone the repo, then symlink each skill into `~/.claude/skills/` for global access across all projects:

```bash
git clone https://github.com/Imbad0202/academic-research-skills.git ~/academic-research-skills
mkdir -p ~/.claude/skills
ln -s ~/academic-research-skills/deep-research ~/.claude/skills/deep-research
ln -s ~/academic-research-skills/academic-paper ~/.claude/skills/academic-paper
ln -s ~/academic-research-skills/academic-paper-reviewer ~/.claude/skills/academic-paper-reviewer
ln -s ~/academic-research-skills/academic-pipeline ~/.claude/skills/academic-pipeline
```

Symlinks mean edits to the repo are reflected immediately. To update: `git pull` inside the repo — no re-linking needed.

For project-scoped installation (skills available only in one project), symlink into `.claude/skills/` relative to the project root instead of `~/.claude/skills/`.
