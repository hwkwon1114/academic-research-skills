# Failure Paths — deep-research Failure Path Map

## Overview

This document lists all failure scenarios for the `socratic` and `lit-review` modes of `deep-research`, along with detection conditions, user notifications, handling steps, and recovery paths.

---

## Failure Path Summary

| # | Failure Scenario | Affected Modes | Severity | Handling Strategy |
|---|---------|---------|---------|---------|
| F1 | Research Frame cannot converge | socratic | Medium | Narrow scope; provide candidate frames |
| F2 | Insufficient literature | lit-review | High | Expand search strategy |
| F4 | Devil's Advocate CRITICAL | lit-review | Critical | STOP + require correction |
| F6 | Socratic dialogue does not converge | socratic | Medium | Re-run with narrower starting question |
| F8 | Only Chinese-language literature available | lit-review | Medium | Switch search strategy |
| F13 | Validator failure (post-emission) | lit-review | High | Report validator stderr; do not claim completion |
| F14 | PDF toolchain absent | lit-review | Low | Save Markdown; print install-message warning |

---

## Detailed Failure Paths

### F1: Research Frame Cannot Converge

**Affected Modes**: `socratic` (Layers 1-3)
**Severity**: Medium

**Trigger Conditions**:
- Layer 1 exceeds 5 rounds; user repeatedly revises the engineering domain without committing
- Layer 2 exceeds 5 rounds; user cannot name a method family or source field
- Layer 3 exceeds 5 rounds; open problem remains vague

**User Notification Message**:
> I notice we've been exploring for a while, but the Research Frame hasn't converged yet. That's okay — let me offer a few possible framings based on what you've shared, and you can tell me which is closest.

**Handling Steps**:
1. Compile the dimensions that have converged (e.g., engineering domain is clear but method family is not)
2. Produce 2-3 candidate framings for the unconverged dimensions
3. Ask the user to select the closest one
4. If user still cannot choose → suggest starting lit-review with a partial frame and narrowing during the investigation phase

**Recovery Paths**:
- User selects a candidate framing → complete remaining layers → emit Research Frame
- User provides a cleaner starting question → restart Socratic from Layer 1
- User accepts a partial frame → emit with `validation_status: frame-partial`, note which fields are uncertain

---

### F2: Insufficient Literature

**Affected Modes**: `lit-review` (Phase 2)
**Severity**: High

**Trigger Conditions**:
- `bibliography_agent` finds < 5 usable sources after standard search strategy
- After excluding quality-unqualified sources, < 3 remain

**User Notification Message**:
> With the current Research Frame, I found only limited relevant literature. This may mean: (1) the cross-field transfer you're looking for is genuinely novel; (2) the search keywords need adjustment; (3) the method family is too specific. Let me try expanding the search strategy.

**Handling Steps**:
1. Expand search keywords (synonyms, broader method family, adjacent source fields)
2. Expand database scope (add grey literature, preprints, workshop papers)
3. Relax the source-field constraint (search for the method family across all fields, not just the named source field)
4. If still insufficient → suggest updating the Research Frame to broaden the method family

**Recovery Paths**:
- Expanded search yields sufficient literature → continue original workflow
- User broadens Research Frame → re-run lit-review with updated frame
- Accept as exploratory → adjust Research Agenda to flag low-evidence directions explicitly

---

### F4: Devil's Advocate CRITICAL

**Affected Modes**: `lit-review` (Checkpoints 1 and 2)
**Severity**: Critical

**Trigger Conditions**:
- `devils_advocate_agent` finds a Critical severity issue at any Checkpoint
- Includes: fatal assumption violation, engineering baseline absent, comparison completeness failure

**User Notification Message**:
> STOP — Devil's Advocate found a critical issue that must be resolved before continuing:
> [Specific issue description]
> This issue fundamentally affects the validity of the Research Agenda directions.

**Handling Steps**:
1. Fully present the Critical issue's description, impact, and suggested correction
2. Pause the workflow; do not advance to the next Phase
3. Wait for user response or correction
4. After user correction → re-execute the Checkpoint
5. Two consecutive CRITICALs → suggest updating the Research Frame

**Recovery Paths**:
- User corrects the issue → re-execute Checkpoint → continue after PASS
- User updates Research Frame → restart lit-review Phase 1
- User accepts the limitation → downgrade to MEDIUM and document in Gap Analysis

---

### F6: Socratic Dialogue Does Not Converge

**Affected Modes**: `socratic`
**Severity**: Medium

**Trigger Conditions**:
- Dialogue exceeds 10 rounds; user still vacillating between different engineering domains or method families
- Extracted INSIGHTs < 3 after 10 rounds

**User Notification Message**:
> We've explored several directions, each with value. I notice we've been moving between framings — this sometimes means the starting question needs to be sharpened. Would you like to:
> (A) Restart Socratic with a narrower starting question (e.g., fix the engineering domain first)
> (B) Accept a partial Research Frame and proceed to lit-review with the dimensions that have converged
> (C) Pause and return later

**Handling Steps**:
1. Compile currently converged dimensions (which of the 3 core fields are settled)
2. Identify the single most-contested dimension
3. Offer the 3 options above
4. If user continues but has not converged by round 15 → auto-compile best available frame and end

**Recovery Paths**:
- Restart with narrower question → restrict to one contested dimension per layer
- Accept partial frame → emit with `validation_status: frame-partial`; proceed to lit-review
- Pause → user can re-invoke socratic at any time

---

### F8: Only Non-English Literature Available

**Affected Modes**: `lit-review` (Phase 2)
**Severity**: Medium

**Trigger Conditions**:
- English academic database searches yield empty or very few results on the cross-field topic
- The source field has primarily non-English literature

**User Notification Message**:
> English-language literature on this cross-field transfer is very limited. I will adjust the search strategy to include broader databases and preprint servers. The Research Agenda will flag directions that rely on limited-language evidence.

**Handling Steps**:
1. Expand search to preprint servers (arXiv, bioRxiv, SSRN) and grey literature
2. Search for adjacent English-language terms that cover the same method family
3. Note the language distribution of the literature in the report
4. If coverage remains thin → mark affected Research Agenda directions as "weak evidence base"

**Recovery Paths**:
- Alternative sources are sufficient → continue workflow with clear language annotations
- Coverage remains thin → Research Agenda Direction 3 (stretch-exploratory) absorbs this as an evidence gap

---

### F13: Validator Failure (Post-Emission)

**Affected Modes**: `lit-review` (Phase 4, post-emission)
**Severity**: High

**Trigger Conditions**:
- `scripts/lit_review_validate.py` exits non-zero after Markdown emission by `report_compiler_agent`

**User Notification Message**:
> The report validator found issues in the generated report. The agent cannot claim completion until these are resolved. Validator output:
> [stderr from lit_review_validate.py]

**Handling Steps**:
1. Report the validator's stderr output to the user verbatim
2. Do NOT claim the report is complete
3. Identify which check failed (per-paper blocks, Research Agenda count, Apply/improve template, PDF gate, Research Frame fields)
4. Fix the identified issue in the report Markdown
5. Re-run the validator until it exits 0

**Recovery Paths**:
- Fix the Markdown and re-validate → proceed to PDF conversion on exit 0
- If validator check #2 fails (wrong direction count): revise Research Agenda to have exactly 3 directions
- If validator check #4 fails (template mismatch): ensure each direction's first non-blank line matches `Apply/improve [X] from [Y] to solve [Z] in [Domain]`

---

### F14: PDF Toolchain Absent

**Affected Modes**: `lit-review` (Phase 4, PDF conversion)
**Severity**: Low

**Trigger Conditions**:
- `scripts/md_to_pdf.py` exits with code 2 (pandoc not found)

**User Notification Message**:
> PDF generation skipped — pandoc not installed. Markdown saved at `reports/<slug>-<date>.md`. Install via `brew install pandoc` (macOS) or `apt install pandoc` (Linux) and re-run `python3 scripts/md_to_pdf.py --input reports/<slug>-<date>.md`.

**Handling Steps**:
1. Confirm the Markdown file was saved successfully to `reports/<slug>-<date>.md`
2. Print the install-message warning (this string is also the sentinel for the validator's `--allow-md-only` mode)
3. Do NOT silently skip — the user must see the warning

**Recovery Paths**:
- User installs pandoc → re-run `python3 scripts/md_to_pdf.py --input <path>` to generate the PDF
- User accepts Markdown-only → the validator accepts this state via `--allow-md-only` when the sentinel is in captured stderr
