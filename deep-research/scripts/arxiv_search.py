#!/usr/bin/env python3
"""
arxiv_search.py — search the arXiv API and emit structured JSON paper records.

Bundled by the deep-research skill so bibliography_agent doesn't have to
re-derive URL encoding, Atom XML parsing, and rate-limit handling on every
invocation. The agent description shrinks to "call this script with the search
terms; parse the JSON it prints".

Rate-limit floor: 3 seconds between calls (arxiv API will 429 below ~1s).
On 429, do NOT retry the same URL — return whatever was already collected
and let the caller fall through to a different source.

Usage:
  python arxiv_search.py --query "additive manufacturing" "machine learning" --max 15 --from 2024
  python arxiv_search.py --query "convergent cross mapping" --max 10
  python arxiv_search.py --query "transfer entropy" "neural network" --from 2023 --json

Output (JSON to stdout, one object per paper):
  [
    {
      "arxiv_id": "2403.12345",
      "title": "...",
      "authors": ["A B", "C D"],
      "year": 2024,
      "published": "2024-03-15",
      "abstract": "...",
      "primary_category": "cs.LG",
      "abs_url": "https://arxiv.org/abs/2403.12345",
      "ar5iv_url": "https://ar5iv.labs.arxiv.org/html/2403.12345"
    },
    ...
  ]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ARXIV_API = "https://export.arxiv.org/api/query"
RATE_LIMIT_SECONDS = 3.0
USER_AGENT = "deep-research-skill/3.2 (https://github.com/hyunwoo-kwon)"
ATOM_NS = "{http://www.w3.org/2005/Atom}"


def build_query(terms: list[str]) -> str:
    """Build an arxiv `search_query=` value from a list of terms.

    Each term becomes `all:"<term>"` (with `"` pre-encoded as `%22` because
    urllib.request does not encode literal quotes for us, and arxiv 400s
    on raw `"` in the query string). Whitespace inside quoted phrases is
    encoded as `+` (arxiv's required form). Multiple terms are AND-combined.
    """
    quoted = []
    for term in terms:
        spaced = term.replace(" ", "+")
        # %22 == " — pre-encoded so the URL is valid as-passed.
        quoted.append(f"all:%22{spaced}%22")
    return "+AND+".join(quoted)


def fetch_atom(query: str, max_results: int) -> str:
    """Fetch the Atom XML response from arxiv. Returns the body or raises."""
    # Note: search_query is built with literal "+" already; do NOT urlencode it
    # again — arxiv rejects double-encoded queries.
    url = (
        f"{ARXIV_API}?search_query={query}"
        f"&max_results={max_results}"
        f"&sortBy=submittedDate&sortOrder=descending"
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_atom(xml_text: str) -> list[dict]:
    """Parse arxiv Atom feed into structured records."""
    root = ET.fromstring(xml_text)
    out: list[dict] = []
    for entry in root.findall(f"{ATOM_NS}entry"):
        # arxiv `<id>` looks like http://arxiv.org/abs/2403.12345v2 — extract base id.
        raw_id = entry.findtext(f"{ATOM_NS}id") or ""
        arxiv_id = raw_id.rsplit("/", 1)[-1]
        # Strip version suffix (v1, v2, ...) so the canonical id matches across versions.
        base_id = arxiv_id.split("v")[0] if "v" in arxiv_id else arxiv_id

        title = (entry.findtext(f"{ATOM_NS}title") or "").strip().replace("\n", " ")
        summary = (entry.findtext(f"{ATOM_NS}summary") or "").strip()
        published = (entry.findtext(f"{ATOM_NS}published") or "").strip()
        year = int(published[:4]) if published[:4].isdigit() else None

        authors = [
            (a.findtext(f"{ATOM_NS}name") or "").strip()
            for a in entry.findall(f"{ATOM_NS}author")
        ]

        primary_category = ""
        cat_el = entry.find("{http://arxiv.org/schemas/atom}primary_category")
        if cat_el is not None:
            primary_category = cat_el.attrib.get("term", "")

        out.append(
            {
                "arxiv_id": base_id,
                "title": title,
                "authors": authors,
                "year": year,
                "published": published[:10],  # YYYY-MM-DD
                "abstract": summary,
                "primary_category": primary_category,
                "abs_url": f"https://arxiv.org/abs/{base_id}",
                "ar5iv_url": f"https://ar5iv.labs.arxiv.org/html/{base_id}",
            }
        )
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Search arXiv and emit JSON records.")
    parser.add_argument(
        "--query",
        nargs="+",
        required=True,
        help="One or more search terms (AND-combined, each treated as a quoted phrase).",
    )
    parser.add_argument("--max", type=int, default=15, help="Max results (default 15).")
    parser.add_argument(
        "--from",
        dest="from_year",
        type=int,
        default=None,
        help="Filter to papers published on or after this year.",
    )
    args = parser.parse_args()

    query = build_query(args.query)

    # Politeness floor — arxiv 429s aggressively if hit faster than ~1s.
    time.sleep(RATE_LIMIT_SECONDS)

    try:
        xml_text = fetch_atom(query, args.max)
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(
                "[]  # arxiv rate-limited (HTTP 429); fall through to a different source",
                file=sys.stderr,
            )
            print("[]")
            return 0
        print(f"arxiv fetch failed: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"arxiv fetch failed: {e}", file=sys.stderr)
        return 1

    papers = parse_atom(xml_text)
    if args.from_year is not None:
        papers = [p for p in papers if p.get("year") and p["year"] >= args.from_year]

    json.dump(papers, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
