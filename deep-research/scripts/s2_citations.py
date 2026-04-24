#!/usr/bin/env python3
"""
s2_citations.py — forward/backward citation graph for a paper via Semantic Scholar.

Used by bibliography_agent during the lineage pass. Given a paper identifier
(arxiv id or DOI), this returns:
  - references: papers this one cites (backward lineage)
  - citations: papers that cite this one (forward lineage)

Each entry is structured with arxiv_id / DOI / title / authors / year / venue /
citation_count so the agent can organize by model family and currency.

Respects S2_API_KEY (raises rate floor from 5s to 1s). Without a key the
unauthenticated API often 429s; the script falls through cleanly and reports
what was retrieved.

Usage:
  python3 s2_citations.py --arxiv-id 2010.08895
  python3 s2_citations.py --doi 10.1145/3580305.3599489
  python3 s2_citations.py --arxiv-id 2010.08895 --limit 20

Output (JSON on stdout):
  {
    "paper": {"title": "...", "authors": [...], "year": 2020, "venue": "..."},
    "references":   [{"arxiv_id": "...", "title": "...", "year": ...}, ...],
    "citations":    [{"arxiv_id": "...", "title": "...", "year": ...}, ...],
    "fetch_log":    ["tried: ... -> result"]
  }
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

USER_AGENT = "deep-research-skill/3.2 (mailto:hwkwon1114@gmail.com)"
S2_API_KEY = os.environ.get("S2_API_KEY")
RATE_FLOOR = 1.0 if S2_API_KEY else 5.0

S2_BASE = "https://api.semanticscholar.org/graph/v1/paper"
FIELDS_REF = "title,authors,year,venue,citationCount,externalIds"


def _http_get_json(url: str, timeout: int = 30) -> tuple[int, dict | list]:
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if S2_API_KEY:
        headers["x-api-key"] = S2_API_KEY
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception:
        return 0, {}


def _paper_key(identifier: str, kind: str) -> str:
    """Build an S2-compatible key: arXiv:<id> or DOI:<doi>."""
    if kind == "arxiv":
        return f"arXiv:{identifier}"
    if kind == "doi":
        return f"DOI:{urllib.parse.quote(identifier, safe='/:')}"
    return identifier


def _slim(entry: dict) -> dict:
    """Extract the fields we care about from an S2 citation/reference entry."""
    if not entry:
        return {}
    paper = entry.get("citedPaper") or entry.get("citingPaper") or entry
    ext = paper.get("externalIds") or {}
    return {
        "arxiv_id": ext.get("ArXiv"),
        "doi": ext.get("DOI"),
        "title": paper.get("title"),
        "authors": [(a.get("name") or "") for a in (paper.get("authors") or [])],
        "year": paper.get("year"),
        "venue": paper.get("venue"),
        "citation_count": paper.get("citationCount"),
    }


def fetch_paper_meta(key: str, log: list[str]) -> dict:
    time.sleep(RATE_FLOOR)
    url = f"{S2_BASE}/{key}?fields=title,authors,year,venue,citationCount,externalIds"
    status, data = _http_get_json(url)
    if status == 429:
        log.append("paper meta: HTTP 429 (rate-limited; set S2_API_KEY for higher limits)")
        return {}
    if status != 200:
        log.append(f"paper meta: HTTP {status}")
        return {}
    return _slim(data)


def fetch_references(key: str, limit: int, log: list[str]) -> list[dict]:
    time.sleep(RATE_FLOOR)
    url = f"{S2_BASE}/{key}/references?fields={FIELDS_REF}&limit={limit}"
    status, data = _http_get_json(url)
    if status != 200:
        log.append(f"references: HTTP {status}")
        return []
    items = data.get("data", []) if isinstance(data, dict) else []
    log.append(f"references: retrieved {len(items)} (requested {limit})")
    return [_slim(i) for i in items]


def fetch_citations(key: str, limit: int, log: list[str]) -> list[dict]:
    time.sleep(RATE_FLOOR)
    url = f"{S2_BASE}/{key}/citations?fields={FIELDS_REF}&limit={limit}"
    status, data = _http_get_json(url)
    if status != 200:
        log.append(f"citations: HTTP {status}")
        return []
    items = data.get("data", []) if isinstance(data, dict) else []
    log.append(f"citations: retrieved {len(items)} (requested {limit})")
    return [_slim(i) for i in items]


def main() -> int:
    parser = argparse.ArgumentParser(description="Forward/backward citation graph for a paper.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--arxiv-id")
    g.add_argument("--doi")
    parser.add_argument("--limit", type=int, default=25, help="max entries per direction (default 25)")
    args = parser.parse_args()

    log: list[str] = []
    if args.arxiv_id:
        key = _paper_key(args.arxiv_id, "arxiv")
    else:
        key = _paper_key(args.doi, "doi")

    paper_meta = fetch_paper_meta(key, log)
    references = fetch_references(key, args.limit, log)
    citations = fetch_citations(key, args.limit, log)

    out = {
        "paper": paper_meta,
        "references": references,
        "citations": citations,
        "fetch_log": log,
    }
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
