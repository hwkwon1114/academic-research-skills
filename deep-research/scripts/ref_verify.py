#!/usr/bin/env python3
"""
ref_verify.py — deterministic existence check for DOIs and arxiv IDs.

Used by source_verification_agent. The agent's prose-level instruction is
"100% DOI verification coverage"; this script makes that verification a
single deterministic call rather than ad-hoc WebFetch per reference.

Closes the "agent fabricated a plausible-looking DOI that doesn't resolve"
failure mode. If the bibliography contains a reference whose DOI 404s or
whose arxiv ID returns no matching entry, this script flags it.

Usage:
  # Single reference
  python3 ref_verify.py --doi 10.1145/3580305.3599489
  python3 ref_verify.py --arxiv-id 2403.12345

  # Batch mode (JSON list on stdin or via --refs-file)
  echo '[{"doi":"10.1145/3580305.3599489"},{"arxiv_id":"2403.12345"}]' | python3 ref_verify.py -

Output (JSON per ref):
  {
    "doi": "10.1145/3580305.3599489",
    "exists": true,
    "canonical": {
      "title": "...",
      "authors": ["..."],
      "year": 2023,
      "venue": "KDD",
      "type": "proceedings-article"
    },
    "source": "crossref",
    "notes": ""
  }

Rate-limit floor: 1 second between Crossref calls, 3 seconds between arxiv calls.
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

USER_AGENT = "deep-research-skill/3.2 (mailto:hwkwon1114@gmail.com)"
CROSSREF_FLOOR = 1.0
ARXIV_FLOOR = 3.0


def _http_get(url: str, timeout: int = 20, accept: str = "application/json") -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": accept})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception:
        return 0, b""


def verify_doi(doi: str) -> dict:
    """Verify a DOI via Crossref. Returns a result dict."""
    time.sleep(CROSSREF_FLOOR)
    url = f"https://api.crossref.org/works/{urllib.parse.quote(doi, safe='/:')}"
    status, body = _http_get(url, accept="application/json")
    if status == 404:
        return {"doi": doi, "exists": False, "source": "crossref", "notes": "Crossref returned 404 — DOI does not resolve"}
    if status != 200:
        return {"doi": doi, "exists": False, "source": "crossref", "notes": f"Crossref returned HTTP {status}"}
    try:
        data = json.loads(body).get("message", {})
    except json.JSONDecodeError:
        return {"doi": doi, "exists": False, "source": "crossref", "notes": "Crossref returned invalid JSON"}
    # Crossref container-title is a list; pick the first.
    container = data.get("container-title") or []
    issued = data.get("issued", {}).get("date-parts", [[None]])[0][0]
    authors = []
    for a in data.get("author", []) or []:
        name = " ".join(filter(None, [a.get("given"), a.get("family")]))
        if name:
            authors.append(name)
    return {
        "doi": doi,
        "exists": True,
        "canonical": {
            "title": (data.get("title") or [""])[0],
            "authors": authors,
            "year": issued,
            "venue": container[0] if container else "",
            "type": data.get("type", ""),
        },
        "source": "crossref",
        "notes": "",
    }


def verify_arxiv(arxiv_id: str) -> dict:
    """Verify an arxiv id via the arxiv API id_list query."""
    time.sleep(ARXIV_FLOOR)
    url = f"https://export.arxiv.org/api/query?id_list={urllib.parse.quote(arxiv_id)}"
    status, body = _http_get(url, accept="application/atom+xml")
    if status != 200 or not body:
        return {"arxiv_id": arxiv_id, "exists": False, "source": "arxiv", "notes": f"arxiv API returned HTTP {status}"}
    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return {"arxiv_id": arxiv_id, "exists": False, "source": "arxiv", "notes": "arxiv returned invalid XML"}
    ns = "{http://www.w3.org/2005/Atom}"
    entry = root.find(f"{ns}entry")
    if entry is None:
        return {"arxiv_id": arxiv_id, "exists": False, "source": "arxiv", "notes": "arxiv: no matching entry"}
    # arxiv returns a stub entry with an error title when the id doesn't exist.
    title = (entry.findtext(f"{ns}title") or "").strip()
    if title.lower().startswith("error"):
        return {"arxiv_id": arxiv_id, "exists": False, "source": "arxiv", "notes": "arxiv: malformed id"}
    published = (entry.findtext(f"{ns}published") or "").strip()
    year = int(published[:4]) if published[:4].isdigit() else None
    authors = [(a.findtext(f"{ns}name") or "").strip() for a in entry.findall(f"{ns}author")]
    return {
        "arxiv_id": arxiv_id,
        "exists": True,
        "canonical": {
            "title": title,
            "authors": authors,
            "year": year,
            "venue": "arXiv",
            "type": "preprint",
        },
        "source": "arxiv",
        "notes": "",
    }


def verify_ref(ref: dict) -> dict:
    """Dispatch a single reference dict to doi or arxiv verification."""
    if ref.get("doi"):
        return verify_doi(ref["doi"])
    if ref.get("arxiv_id"):
        return verify_arxiv(ref["arxiv_id"])
    return {"exists": False, "notes": "no doi or arxiv_id field present", "ref": ref}


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify DOIs and arxiv IDs exist.")
    g = parser.add_mutually_exclusive_group(required=False)
    g.add_argument("--doi")
    g.add_argument("--arxiv-id")
    g.add_argument("--refs-file", help="path to JSON file with list of refs")
    parser.add_argument(
        "batch_stdin",
        nargs="?",
        default=None,
        help="pass '-' to read JSON list of refs from stdin",
    )
    args = parser.parse_args()

    if args.doi:
        out = verify_doi(args.doi)
    elif args.arxiv_id:
        out = verify_arxiv(args.arxiv_id)
    elif args.refs_file:
        with open(args.refs_file) as f:
            refs = json.load(f)
        out = [verify_ref(r) for r in refs]
    elif args.batch_stdin == "-":
        refs = json.load(sys.stdin)
        out = [verify_ref(r) for r in refs]
    else:
        parser.print_help(sys.stderr)
        return 2

    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
