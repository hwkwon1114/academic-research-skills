#!/usr/bin/env python3
"""
vault_lint.py — pre-flight check on a synthesize staging bundle.

After report_compiler_agent emits a two-file bundle (a Synthesized Paper at
`syntheses/_staging/<slug>.md` plus N Paper stubs at
`syntheses/_staging/sources/<paper-slug>.md`), this script verifies the
bidirectional-lint invariant holds BEFORE the bundle reaches the user's
ACCEPT gate.

Checks:
  1. Every `[[paper-slug#claim-id]]` wikilink in the synthesis body resolves
     to a stub whose `extracted_claims[]` actually contains that claim-id.
  2. Every `[[paper-slug]]` in the synthesis `sources:` has a corresponding
     stub file at `sources/paper-slug.md`.
  3. Each stub's frontmatter is valid YAML and has the required keys.
  4. Claim IDs within each stub are unique.
  5. No orphan stubs (stubs that the synthesis never references).

Exits non-zero on lint failure, with a per-violation report. Used either as
a pre-emit self-check inside report_compiler_agent or as a CI-style check on
a staging directory before ACCEPT.

Usage:
  python3 vault_lint.py --synthesis-path syntheses/_staging/neural-operators.md
  # ...checks both the synthesis and its sibling sources/ folder

Output: JSON on stdout.
  {
    "passed": true|false,
    "violations": [{"kind": "...", "detail": "..."}, ...],
    "summary": {"stubs_found": N, "claim_refs_checked": N, "unresolved": N}
  }
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLAIM_REF_RE = re.compile(r"\[\[([A-Za-z0-9_.-]+)#([A-Za-z0-9_.-]+)(?:\|[^\]]+)?\]\]")
PAPER_LINK_RE = re.compile(r"\[\[([A-Za-z0-9_.-]+)\]\]")

SYNTH_REQUIRED_KEYS = {"type", "topic", "generated_by", "deep-research-agents-used", "sources"}
STUB_REQUIRED_KEYS = {"type", "authors", "year", "venue", "url_or_path", "review_status", "extracted_claims"}


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Very light YAML parser — enough for our flat schema.

    Not a real YAML parser. Handles:
      - `key: value` pairs
      - `key:` followed by indented `- item` list entries
      - `key:` followed by indented `- id: ...\\n  quote: ...` object-list entries

    Returns (frontmatter_dict, body_text).
    """
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm_raw = text[4:end]
    body = text[end + 5 :]

    fm: dict = {}
    current_key = None
    current_list: list | None = None
    current_obj: dict | None = None

    for line in fm_raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        # Top-level `key: value` or `key:`
        top_match = re.match(r"^([A-Za-z_][\w-]*):(\s*(.*))?$", line)
        if top_match and not line.startswith(" "):
            current_key = top_match.group(1)
            inline_value = (top_match.group(3) or "").strip()
            if inline_value:
                # Strip simple quotes
                inline_value = inline_value.strip("\"'")
                fm[current_key] = inline_value
                current_list = None
                current_obj = None
            else:
                fm[current_key] = []
                current_list = fm[current_key]
                current_obj = None
            continue

        stripped = line.strip()

        # List entry starting with `- key: value` or `- "string"`
        if stripped.startswith("- "):
            item_content = stripped[2:].strip()
            if current_list is None:
                # Coerce the existing scalar key into a list.
                if current_key is not None:
                    fm[current_key] = []
                    current_list = fm[current_key]
            # Detect `- key: value` → start a new dict entry
            kv_match = re.match(r"^([A-Za-z_][\w-]*):(\s*(.*))?$", item_content)
            if kv_match:
                current_obj = {}
                k = kv_match.group(1)
                v = (kv_match.group(3) or "").strip().strip("\"'")
                if v:
                    current_obj[k] = v
                current_list.append(current_obj)
            else:
                current_list.append(item_content.strip("\"'"))
                current_obj = None
            continue

        # Continuation of a dict entry in a list: indented `key: value`
        if current_obj is not None and line.startswith("  ") and not line.startswith("  - "):
            kv_match = re.match(r"^\s+([A-Za-z_][\w-]*):(\s*(.*))?$", line)
            if kv_match:
                k = kv_match.group(1)
                v = (kv_match.group(3) or "").strip().strip("\"'")
                current_obj[k] = v
                continue

        # Nested list under a dict entry key (indented `  - value`)
        if current_obj is not None and line.startswith("      - "):
            k = list(current_obj.keys())[-1] if current_obj else None
            if k:
                if not isinstance(current_obj.get(k), list):
                    current_obj[k] = []
                current_obj[k].append(line.split("- ", 1)[1].strip().strip("\"'"))
            continue

    return fm, body


def _load_paper_page(path: Path) -> dict | None:
    """Load frontmatter from an accepted vault Paper page. Returns None if unreadable."""
    try:
        fm, _ = parse_frontmatter(path.read_text())
        return fm if fm else None
    except OSError:
        return None


def lint_bundle(synthesis_path: Path, vault_path: Path | None = None) -> dict:
    violations: list[dict] = []
    synthesis_text = synthesis_path.read_text()
    fm, body = parse_frontmatter(synthesis_text)

    # Check synthesis frontmatter
    if fm.get("type") != "synthesized-paper":
        violations.append({"kind": "wrong_type", "detail": f"synthesis frontmatter `type` is {fm.get('type')!r}, expected 'synthesized-paper'"})
    missing = SYNTH_REQUIRED_KEYS - set(fm.keys())
    if missing:
        violations.append({"kind": "missing_synthesis_keys", "detail": f"missing keys: {sorted(missing)}"})

    # Explicit forbidden key: extracted_claims must NOT live on synthesis (v3.2 amended contract)
    if "extracted_claims" in fm:
        violations.append({"kind": "forbidden_key", "detail": "Synthesized Paper must not carry `extracted_claims` — claim-level provenance lives on Paper stubs"})

    # Load all stubs under sources/
    sources_dir = synthesis_path.parent / "sources"
    stubs: dict[str, dict] = {}
    if sources_dir.is_dir():
        for stub_path in sources_dir.glob("*.md"):
            slug = stub_path.stem
            stub_fm, _ = parse_frontmatter(stub_path.read_text())
            stubs[slug] = stub_fm

            # Check each stub's keys + claim-id uniqueness
            if stub_fm.get("type") != "paper":
                violations.append({"kind": "stub_wrong_type", "detail": f"{slug}: type is {stub_fm.get('type')!r}, expected 'paper'"})
            miss = STUB_REQUIRED_KEYS - set(stub_fm.keys())
            if miss:
                violations.append({"kind": "stub_missing_keys", "detail": f"{slug}: missing {sorted(miss)}"})
            claim_ids: list[str] = []
            for claim in stub_fm.get("extracted_claims", []) or []:
                cid = claim.get("id") if isinstance(claim, dict) else None
                if cid:
                    claim_ids.append(cid)
            dupes = [cid for cid in claim_ids if claim_ids.count(cid) > 1]
            if dupes:
                violations.append({"kind": "duplicate_claim_id", "detail": f"{slug}: duplicate claim IDs: {sorted(set(dupes))}"})

    # Load accepted vault Paper pages (papers/ in the vault root) so that wikilinks
    # citing already-accepted papers resolve without needing a staging stub.
    vault_papers: dict[str, dict] = {}
    if vault_path is not None:
        papers_dir = vault_path / "papers"
        if papers_dir.is_dir():
            for paper_path in papers_dir.glob("*.md"):
                slug = paper_path.stem
                if slug not in stubs:  # staging stub takes precedence if present
                    page_fm = _load_paper_page(paper_path)
                    if page_fm is not None:
                        vault_papers[slug] = page_fm

    # Combined lookup: staging stubs first, then accepted vault pages
    all_paper_sources = {**vault_papers, **stubs}

    # Check every `[[paper-slug#claim-id]]` in the body resolves to a stub or accepted page
    claim_refs_in_body = CLAIM_REF_RE.findall(body)
    checked = 0
    unresolved = 0
    for paper_slug, claim_id in claim_refs_in_body:
        checked += 1
        source = all_paper_sources.get(paper_slug)
        if not source:
            location = "sources/{paper_slug}.md or {vault_path}/papers/{paper_slug}.md" if vault_path else f"sources/{paper_slug}.md"
            violations.append({"kind": "unresolved_paper_slug", "detail": f"body cites `[[{paper_slug}#{claim_id}]]` but no paper page found at {location}"})
            unresolved += 1
            continue
        source_claim_ids = {c.get("id") for c in (source.get("extracted_claims") or []) if isinstance(c, dict)}
        if claim_id not in source_claim_ids:
            origin = "vault papers/" if paper_slug in vault_papers else "staging sources/"
            violations.append({"kind": "unresolved_claim_id", "detail": f"body cites `[[{paper_slug}#{claim_id}]]` but {origin}{paper_slug} has claim IDs {sorted(source_claim_ids)}"})
            unresolved += 1

    # Check every source in `sources:` has a stub or an accepted vault page
    for src in fm.get("sources", []) or []:
        m = PAPER_LINK_RE.match(str(src))
        if m:
            slug = m.group(1)
            if slug not in all_paper_sources:
                hint = " (or in vault papers/ if --vault-path is set)" if vault_path is None else ""
                violations.append({"kind": "missing_stub_for_source", "detail": f"`sources:` lists [[{slug}]] but no stub at sources/{slug}.md{hint}"})

    # Check for orphan stubs (staging stubs not referenced anywhere in the synthesis)
    body_slugs = set(s for (s, _) in claim_refs_in_body)
    listed_sources = set()
    for src in fm.get("sources", []) or []:
        m = PAPER_LINK_RE.match(str(src))
        if m:
            listed_sources.add(m.group(1))
    for slug in stubs:  # only staging stubs can be orphans; vault pages are pre-existing
        if slug not in body_slugs and slug not in listed_sources:
            violations.append({"kind": "orphan_stub", "detail": f"sources/{slug}.md exists but is never cited by the synthesis"})

    summary = {
        "stubs_found": len(stubs),
        "vault_pages_used": len(vault_papers),
        "claim_refs_checked": checked,
        "unresolved": unresolved,
        "violations_count": len(violations),
    }
    return {"passed": len(violations) == 0, "violations": violations, "summary": summary}


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint a synthesize staging bundle.")
    parser.add_argument("--synthesis-path", required=True, help="path to syntheses/_staging/<slug>.md")
    parser.add_argument("--vault-path", default=None,
                        help="root of the Research Vault (e.g. ~/Documents/Research Vault). "
                             "When set, wikilinks to already-accepted papers/ pages resolve "
                             "without requiring a staging stub, so synthesize runs that skip "
                             "re-stubbing known papers still pass lint.")
    args = parser.parse_args()

    path = Path(args.synthesis_path)
    if not path.is_file():
        print(json.dumps({"passed": False, "violations": [{"kind": "file_not_found", "detail": str(path)}]}))
        return 2

    vault_path = Path(args.vault_path).expanduser() if args.vault_path else None
    result = lint_bundle(path, vault_path=vault_path)
    json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
