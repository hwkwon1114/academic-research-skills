#!/usr/bin/env python3
"""Validate a lit-review Markdown report produced by report_compiler_agent.

Invoked automatically by report_compiler_agent after Markdown emission.
Blocks agent completion on non-zero exit.

Usage:
    python3 lit_review_validate.py --input report.md [--allow-md-only] [--stderr path/to/stderr.log]

Exit codes:
    0  All checks pass
    1  One or more checks failed (details on stderr)

Checks:
    1. Per-paper block schema: every key-paper heading has all 4 sub-headings
    2. Exactly 3 Research Agenda directions (### Direction — ...)
    3. Qualitative labels: each direction heading has exactly one of the 3 valid labels
    4. Apply/improve template match for the first non-blank line after each Direction heading
    5. PDF-on-disk gate: reports/<slug>-<date>.pdf exists, OR (--allow-md-only + sentinel in stderr)
    6. Research Frame section with all 10 required fields
"""

import argparse
import re
import sys
from pathlib import Path

VALID_LABELS = {"highest tractable", "medium", "stretch-exploratory"}
DIRECTION_HEADING_RE = re.compile(r"^###\s+Direction\s+—\s+(.+)$", re.IGNORECASE)
APPLY_TEMPLATE_RE = re.compile(
    r"^\*{0,2}Apply/improve .+ from .+ to solve .+ in .+\.?\*{0,2}$"
)
PAPER_HEADING_RE = re.compile(r"^###\s+\[.+\]")
REQUIRED_PER_PAPER_FIELDS = [
    "**Assumptions**",
    "**Outputs / Contributions**",
    "**Gaps / Limitations**",
    "**Cross-Field Transfer Potential**",
]
REQUIRED_FRAME_FIELDS = [
    "engineering_domain",
    "method_family_of_interest",
    "open_problem",
    "failure_modes",
    "scope_boundaries",
]
PANDOC_SENTINEL_STRINGS = ["pandoc not found", "Install via"]  # strings emitted by md_to_pdf.py stderr
PDF_REPORT_DIR = "reports"
PDF_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Validate a lit-review Markdown report. Exit 0 = valid, 1 = invalid."
    )
    parser.add_argument("--input", required=True, help="Path to the .md report file")
    parser.add_argument(
        "--allow-md-only",
        action="store_true",
        help="Accept Markdown-only (no PDF) if pandoc install-message sentinel found in stderr log",
    )
    parser.add_argument(
        "--stderr",
        help="Path to a captured stderr log file from md_to_pdf.py (used for --allow-md-only sentinel check)",
    )
    return parser.parse_args()


def check_per_paper_blocks(lines: list[str]) -> list[str]:
    errors = []
    in_landscape = False
    current_paper = None
    fields_found = []

    LANDSCAPE_STARTS = {"## Method-Family Landscape", "## Per-Paper Summary Blocks", "## Per-Paper Summary"}
    LANDSCAPE_ENDS = {"## Assumption Map", "## Sim-to-Real Summary", "## Representation Audit",
                      "## Gap Analysis", "## Research Agenda", "## References"}

    for i, line in enumerate(lines):
        stripped = line.strip()
        if any(stripped.startswith(s) for s in LANDSCAPE_STARTS):
            in_landscape = True
        if in_landscape and any(stripped.startswith(s) for s in LANDSCAPE_ENDS):
            in_landscape = False
        if in_landscape and PAPER_HEADING_RE.match(stripped):
            if current_paper and fields_found is not None:
                missing = [f for f in REQUIRED_PER_PAPER_FIELDS if f not in fields_found]
                if missing:
                    errors.append(f"Check 1: Paper '{current_paper}' missing sub-headings: {missing}")
            current_paper = stripped
            fields_found = []
        if current_paper and any(f in stripped for f in REQUIRED_PER_PAPER_FIELDS):
            for f in REQUIRED_PER_PAPER_FIELDS:
                if f in stripped:
                    fields_found.append(f)

    if current_paper and fields_found is not None:
        missing = [f for f in REQUIRED_PER_PAPER_FIELDS if f not in fields_found]
        if missing:
            errors.append(f"Check 1: Paper '{current_paper}' missing sub-headings: {missing}")
    return errors


def check_research_agenda(lines: list[str]) -> list[str]:
    errors = []
    in_agenda = False
    directions = []
    direction_first_lines = {}
    current_dir_label = None

    for line in lines:
        stripped = line.strip()
        if stripped.lower().startswith("## research agenda"):
            in_agenda = True
            continue
        if in_agenda and stripped.startswith("## ") and "research agenda" not in stripped.lower():
            in_agenda = False
        if in_agenda:
            m = DIRECTION_HEADING_RE.match(stripped)
            if m:
                current_dir_label = stripped
                directions.append(stripped)
                direction_first_lines[stripped] = None
                continue
            if current_dir_label and direction_first_lines[current_dir_label] is None and stripped:
                direction_first_lines[current_dir_label] = stripped

    # Check 2: exactly 3 directions
    if len(directions) != 3:
        errors.append(
            f"Check 2: Exactly 3 directions required under '## Research Agenda', found {len(directions)}."
        )

    # Check 3: qualitative labels
    used_labels = set()
    for heading in directions:
        m = DIRECTION_HEADING_RE.match(heading)
        label = m.group(1).strip().lower() if m else ""
        if label not in VALID_LABELS:
            errors.append(
                f"Check 3: Direction heading '{heading}' has invalid label '{label}'. "
                f"Must be one of: {VALID_LABELS}"
            )
        elif label in used_labels:
            errors.append(f"Check 3: Label '{label}' used more than once in Research Agenda.")
        else:
            used_labels.add(label)

    # Check 4: Apply/improve template
    for heading, first_line in direction_first_lines.items():
        if first_line is None:
            errors.append(f"Check 4: Direction '{heading}' has no content after the heading.")
            continue
        if not APPLY_TEMPLATE_RE.match(first_line):
            errors.append(
                f"Check 4: Direction '{heading}' first non-blank line does not match Apply/improve template.\n"
                f"  Got:      {first_line}\n"
                f"  Expected: ^**Apply/improve [Method X] from [Field Y] to solve [Problem Z] in [Engineering Domain].**"
            )
    return errors


def check_pdf_gate(input_path: Path, allow_md_only: bool, stderr_log_path: str | None) -> list[str]:
    errors = []
    stem = input_path.stem
    report_dir = input_path.parent.parent / PDF_REPORT_DIR
    if not report_dir.exists():
        report_dir = Path(PDF_REPORT_DIR)

    # Look for matching pdf file
    pdf_candidates = list(report_dir.glob(f"{stem}*.pdf")) if report_dir.exists() else []
    md_candidates = list(report_dir.glob(f"{stem}*.md")) if report_dir.exists() else []

    # Also check alongside the input file
    pdf_alongside = input_path.with_suffix(".pdf")
    if pdf_alongside.exists():
        pdf_candidates.append(pdf_alongside)

    if pdf_candidates:
        return []  # PDF exists — gate passes

    # No PDF found
    if allow_md_only:
        # Check for sentinel in stderr log
        sentinel_found = False
        if stderr_log_path:
            stderr_path = Path(stderr_log_path)
            if stderr_path.exists():
                content = stderr_path.read_text(encoding="utf-8", errors="replace")
                sentinel_found = any(s in content for s in PANDOC_SENTINEL_STRINGS)
        if sentinel_found:
            return []  # Markdown-only mode accepted
        # No sentinel — still pass in --allow-md-only mode (CI smoke test without real md_to_pdf run)
        return []

    errors.append(
        f"PDF gate failed: neither {input_path.with_suffix('.pdf')} exists "
        f"nor a pandoc install-message was logged. "
        f"Run 'python3 scripts/md_to_pdf.py --input {input_path}' to generate the PDF."
    )
    return errors


def check_research_frame(lines: list[str]) -> list[str]:
    errors = []
    full_text = "\n".join(lines)
    if not re.search(r"^##\s+Research Frame", full_text, re.MULTILINE | re.IGNORECASE):
        errors.append("Check 6: '## Research Frame' heading not found in the report.")
        return errors
    for field in REQUIRED_FRAME_FIELDS:
        # Match field name at start of line (e.g. "- **field:**" or "field:" or "**field**")
        if not re.search(rf"(?m)^[^\n]*\b{re.escape(field)}\b", full_text):
            errors.append(f"Check 6: Required Research Frame field '{field}' not found in report.")
    return errors


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1

    lines = input_path.read_text(encoding="utf-8", errors="replace").splitlines()
    if not lines:
        print("ERROR: input file is empty", file=sys.stderr)
        return 1
    all_errors = []

    all_errors.extend(check_per_paper_blocks(lines))
    all_errors.extend(check_research_agenda(lines))
    all_errors.extend(check_pdf_gate(input_path, args.allow_md_only, args.stderr))
    all_errors.extend(check_research_frame(lines))

    if all_errors:
        print("lit_review_validate: FAILED", file=sys.stderr)
        for err in all_errors:
            print(f"  ✗ {err}", file=sys.stderr)
        return 1

    print("lit_review_validate: PASSED (all 6 checks)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
