#!/usr/bin/env python3
"""
paper_fetch.py — implement the deep-research full-text retrieval ladder.

This is the script form of the `paper_fetch_agent` retrieval ladder. The agent
description tells the model WHEN to call this; the script does the work. By
keeping the ladder in code we get:
  - Honest, fixed retrieval quality classification (no model wishful thinking)
  - File-based caching so the same paper isn't refetched within a session
  - Rate-limit floors per source
  - Single source of truth — every downstream agent sees the same body text

Output is YAML on stdout with the contract documented in
`agents/paper_fetch_agent.md § Outputs`.

Ladder, in order:
  1. arxiv source `.tar.gz`         — authoritative for arxiv papers
  2. ar5iv HTML                     — arxiv fallback when source unavailable
  3. biorxiv / medrxiv direct       — for DOI prefix 10.1101 (biology preprints)
  4. openreview.net PDF             — for NeurIPS/ICML/ICLR openreview papers
  5. OpenAlex OA PDF + pdftotext    — legal OA via DOI; parsed to text if pdftotext is installed
  6. Unpaywall OA PDF + pdftotext   — second legal OA resolver
  7. Sci-Hub (OPT-IN via SCI_HUB_MIRROR env var) — paywalled-paper shadow library; disabled by default
  8. Semantic Scholar abstract      — abstract-only fallback
  9. WebSearch metadata             — last-resort metadata-only

Environment variables:
  DEEP_RESEARCH_CACHE=0     disable cache for this call
  DEEP_RESEARCH_CACHE_DIR   override cache directory (default ~/.cache/deep-research/paper-fetch)
  S2_API_KEY                Semantic Scholar API key (raises rate limit from 5s→1s floor)
  UNPAYWALL_EMAIL           contact email for Unpaywall API (required per their TOS)
  SCI_HUB_MIRROR            If set (e.g. https://sci-hub.xyz), enables the opt-in Sci-Hub rung.
                            Leave UNSET to keep the rung disabled — the default. The script will
                            never silently reach out to Sci-Hub without your explicit opt-in.
                            Legal/ethical tradeoffs are your call; see README for details.

Usage:
  python paper_fetch.py --arxiv-id 2403.12345
  python paper_fetch.py --doi 10.1145/3580305.3599489
  python paper_fetch.py --url https://arxiv.org/abs/2403.12345
  python paper_fetch.py --title "Convergent Cross Mapping" --author "Sugihara" --year 2012

Cache: ~/.cache/deep-research/paper-fetch/<paper_id>.yaml
       Set DEEP_RESEARCH_CACHE=0 to disable the cache for this call.

Rate limit floors (seconds between requests, per source):
  arxiv 3s | semantic-scholar 5s (1s with API key) | openalex 1s | unpaywall 1s
"""
from __future__ import annotations

import argparse
import io
import json
import os
import re
import sys
import tarfile
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

USER_AGENT = "deep-research-skill/3.2 (mailto:hwkwon1114@gmail.com)"
CACHE_DIR = Path(os.environ.get("DEEP_RESEARCH_CACHE_DIR", "~/.cache/deep-research/paper-fetch")).expanduser()
CACHE_TTL_FULLTEXT_S = 7 * 24 * 3600
CACHE_TTL_OTHER_S = 24 * 3600
CACHE_ENABLED = os.environ.get("DEEP_RESEARCH_CACHE", "1") != "0"

S2_API_KEY = os.environ.get("S2_API_KEY")
UNPAYWALL_EMAIL = os.environ.get("UNPAYWALL_EMAIL", "research@example.invalid")
SCI_HUB_MIRROR = os.environ.get("SCI_HUB_MIRROR", "").rstrip("/")  # empty string → Sci-Hub rung is disabled


# ----------------------------- PDF to text -----------------------------------


def pdf_to_text(pdf_bytes: bytes) -> str | None:
    """Convert PDF bytes to plain text using the pdftotext CLI, if available.

    Returns None if pdftotext is not installed (graceful degradation — the caller
    then returns retrieval_quality=body-partial with a "bytes fetched but not parsed"
    note). Install on macOS via `brew install poppler`; on Debian via
    `apt install poppler-utils`.
    """
    import shutil
    import subprocess
    import tempfile

    if shutil.which("pdftotext") is None:
        return None
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name
        # -layout preserves reading order across columns; -enc UTF-8 avoids mojibake.
        result = subprocess.run(
            ["pdftotext", "-layout", "-enc", "UTF-8", tmp_path, "-"],
            capture_output=True,
            timeout=30,
        )
        os.unlink(tmp_path)
        if result.returncode != 0:
            return None
        return result.stdout.decode("utf-8", errors="replace")
    except (subprocess.TimeoutExpired, OSError):
        return None


# ----------------------------- helpers ----------------------------------------


def _http_get(url: str, timeout: int = 30, accept: str | None = None) -> tuple[int, bytes, dict]:
    """GET a URL. Returns (status, body, headers). Never raises on HTTP errors."""
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    if S2_API_KEY and "semanticscholar.org" in url:
        headers["x-api-key"] = S2_API_KEY
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.getcode(), resp.read(), dict(resp.headers)
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        return e.code, body, dict(e.headers or {})
    except Exception as e:
        return 0, str(e).encode(), {}


def _yaml_dump(obj) -> str:
    """Minimal YAML emitter — enough for our flat output structure."""
    out: list[str] = []

    def emit(key: str, val):
        if isinstance(val, str) and ("\n" in val or len(val) > 80):
            out.append(f"{key}: |")
            for line in val.splitlines() or [""]:
                out.append(f"  {line}")
        elif isinstance(val, list):
            if not val:
                out.append(f"{key}: []")
            else:
                out.append(f"{key}:")
                for v in val:
                    if isinstance(v, str):
                        # Quote strings that contain colons or special chars
                        s = v.replace('"', '\\"')
                        out.append(f'  - "{s}"')
                    else:
                        out.append(f"  - {v}")
        elif isinstance(val, bool):
            out.append(f"{key}: {'true' if val else 'false'}")
        elif val is None:
            out.append(f"{key}: null")
        else:
            s = str(val).replace('"', '\\"')
            if isinstance(val, (int, float)):
                out.append(f"{key}: {val}")
            else:
                out.append(f'{key}: "{s}"')

    for k, v in obj.items():
        emit(k, v)
    return "\n".join(out) + "\n"


def _cache_key(paper_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]+", "_", paper_id)
    return CACHE_DIR / f"{safe}.yaml"


def _read_cache(paper_id: str) -> dict | None:
    if not CACHE_ENABLED:
        return None
    p = _cache_key(paper_id)
    if not p.exists():
        return None
    age = time.time() - p.stat().st_mtime
    # We don't know the quality without parsing — use the conservative TTL.
    if age > CACHE_TTL_OTHER_S:
        # Conservative: evict if older than 1d. Full-text papers will refetch
        # but that's preferable to serving stale paywall fallbacks.
        return None
    try:
        # Cheap parse: just look for `retrieval_quality: ...` and trust the cache.
        text = p.read_text()
        return {"_cached_text": text}
    except Exception:
        return None


def _write_cache(paper_id: str, yaml_text: str) -> None:
    if not CACHE_ENABLED:
        return
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _cache_key(paper_id).write_text(yaml_text)


# ----------------------------- HTML to text ------------------------------------


class _HTMLToText(HTMLParser):
    """Strip HTML to readable plain text. Preserves paragraph breaks."""

    SKIP = {"script", "style", "head", "nav", "footer"}
    BLOCK = {"p", "div", "br", "h1", "h2", "h3", "h4", "h5", "h6", "li", "tr"}

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.stack: list[str] = []

    def handle_starttag(self, tag, attrs):
        self.stack.append(tag)

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if tag in self.BLOCK:
            self.parts.append("\n")
        if tag in {"h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data):
        if any(t in self.SKIP for t in self.stack):
            return
        self.parts.append(data)

    def text(self) -> str:
        raw = "".join(self.parts)
        # Collapse 3+ newlines to 2.
        raw = re.sub(r"\n{3,}", "\n\n", raw)
        # Collapse runs of horizontal whitespace.
        raw = re.sub(r"[ \t]+", " ", raw)
        return raw.strip()


def html_to_text(html: str) -> str:
    p = _HTMLToText()
    p.feed(html)
    return p.text()


# ----------------------------- ladder rungs -----------------------------------


def fetch_arxiv_source(arxiv_id: str, log: list[str]) -> str | None:
    """Rung 1: download arxiv .tar.gz, extract main .tex, return raw LaTeX."""
    url = f"https://arxiv.org/e-print/{arxiv_id}"
    time.sleep(3.0)
    status, body, _ = _http_get(url, timeout=60)
    if status != 200 or not body:
        log.append(f"tried: arxiv source ({url}) -> HTTP {status}")
        return None
    try:
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tar:
            members = [m for m in tar.getmembers() if m.name.endswith(".tex")]
            # Prefer the largest .tex file (usually the main document).
            members.sort(key=lambda m: m.size, reverse=True)
            if not members:
                log.append("tried: arxiv source -> tar contained no .tex files")
                return None
            main = tar.extractfile(members[0])
            if main is None:
                return None
            tex = main.read().decode("utf-8", errors="replace")
            log.append(f"tried: arxiv source .tar.gz -> success (LaTeX, {len(tex)} chars)")
            return tex
    except (tarfile.TarError, OSError) as e:
        log.append(f"tried: arxiv source -> untar failed: {e}")
        return None


def fetch_ar5iv(arxiv_id: str, log: list[str]) -> str | None:
    """Rung 2: ar5iv HTML rendering of an arxiv paper."""
    url = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
    time.sleep(3.0)
    status, body, _ = _http_get(url, timeout=60, accept="text/html")
    if status != 200 or not body:
        log.append(f"tried: ar5iv ({url}) -> HTTP {status}")
        return None
    text = html_to_text(body.decode("utf-8", errors="replace"))
    if len(text) < 1000:
        log.append(f"tried: ar5iv -> body too short ({len(text)} chars)")
        return None
    log.append(f"tried: ar5iv -> success (HTML->text, {len(text)} chars)")
    return text


def fetch_openalex_oa(doi: str, log: list[str]) -> tuple[str | None, dict]:
    """Rung 3: OpenAlex metadata + open-access PDF resolver. Returns (text, metadata)."""
    url = f"https://api.openalex.org/works/doi:{urllib.parse.quote(doi)}"
    time.sleep(1.0)
    status, body, _ = _http_get(url, timeout=30, accept="application/json")
    if status != 200:
        log.append(f"tried: openalex ({url}) -> HTTP {status}")
        return None, {}
    try:
        meta = json.loads(body)
    except json.JSONDecodeError:
        log.append("tried: openalex -> invalid JSON")
        return None, {}

    oa = meta.get("open_access") or {}
    if not oa.get("is_oa"):
        log.append("tried: openalex -> paper is not open-access (no PDF available)")
        return None, meta
    pdf_url = oa.get("oa_url")
    if not pdf_url:
        log.append("tried: openalex -> is_oa but no oa_url")
        return None, meta

    time.sleep(1.0)
    status, pdf_body, headers = _http_get(pdf_url, timeout=60)
    if status != 200 or not pdf_body:
        log.append(f"tried: openalex OA PDF ({pdf_url}) -> HTTP {status}")
        return None, meta
    # Try to parse the PDF with pdftotext. If it's not installed, return the
    # bytes-marker so downstream sees body-partial with an honest note.
    extracted = pdf_to_text(pdf_body)
    if extracted and len(extracted) > 500:
        log.append(
            f"tried: openalex OA PDF + pdftotext -> success "
            f"({len(pdf_body)} PDF bytes -> {len(extracted)} chars of text)"
        )
        return extracted, meta
    log.append(
        f"tried: openalex OA PDF -> got {len(pdf_body)} bytes "
        f"(pdftotext {'extracted too little' if extracted else 'not installed'}; returning body-partial)"
    )
    return f"[PDF body fetched from {pdf_url}, {len(pdf_body)} bytes — install pdftotext (brew install poppler) to extract text]", meta


def fetch_unpaywall(doi: str, log: list[str]) -> tuple[str | None, dict]:
    url = f"https://api.unpaywall.org/v2/{urllib.parse.quote(doi)}?email={UNPAYWALL_EMAIL}"
    time.sleep(1.0)
    status, body, _ = _http_get(url, timeout=30, accept="application/json")
    if status != 200:
        log.append(f"tried: unpaywall -> HTTP {status}")
        return None, {}
    try:
        meta = json.loads(body)
    except json.JSONDecodeError:
        log.append("tried: unpaywall -> invalid JSON")
        return None, {}
    best = meta.get("best_oa_location") or {}
    pdf_url = best.get("url_for_pdf") or best.get("url")
    if not pdf_url:
        log.append("tried: unpaywall -> no OA copy listed")
        return None, meta
    time.sleep(1.0)
    status, pdf_body, _ = _http_get(pdf_url, timeout=60)
    if status != 200 or not pdf_body:
        log.append(f"tried: unpaywall OA PDF -> HTTP {status}")
        return None, meta
    extracted = pdf_to_text(pdf_body)
    if extracted and len(extracted) > 500:
        log.append(
            f"tried: unpaywall OA PDF + pdftotext -> success "
            f"({len(pdf_body)} PDF bytes -> {len(extracted)} chars of text)"
        )
        return extracted, meta
    log.append(
        f"tried: unpaywall OA PDF -> got {len(pdf_body)} bytes "
        f"(pdftotext {'extracted too little' if extracted else 'not installed'}; returning body-partial)"
    )
    return f"[PDF body fetched from {pdf_url}, {len(pdf_body)} bytes — install pdftotext to extract text]", meta


def fetch_biorxiv(doi_or_url: str, log: list[str]) -> tuple[str | None, dict]:
    """Rung for biorxiv / medrxiv preprints. DOIs in these servers start with 10.1101/.

    Approach: fetch the landing page and look for the `citation_pdf_url` meta tag,
    which points at the preprint PDF. Then download + pdftotext.
    """
    # Normalize to a landing-page URL. biorxiv and medrxiv share the same metadata pattern.
    if doi_or_url.startswith("10.1101/"):
        # Try biorxiv first; if that 404s, try medrxiv.
        candidates = [
            f"https://www.biorxiv.org/content/{doi_or_url}v1",
            f"https://www.medrxiv.org/content/{doi_or_url}v1",
        ]
    else:
        candidates = [doi_or_url]

    for landing_url in candidates:
        time.sleep(1.0)
        status, body, _ = _http_get(landing_url, timeout=30, accept="text/html")
        if status != 200 or not body:
            log.append(f"tried: biorxiv/medrxiv landing ({landing_url}) -> HTTP {status}")
            continue
        html = body.decode("utf-8", errors="replace")
        pdf_m = re.search(r'<meta name="citation_pdf_url" content="([^"]+)"', html)
        title_m = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
        year_m = re.search(r'<meta name="citation_publication_date" content="([0-9]{4})', html)
        if not pdf_m:
            log.append(f"tried: biorxiv/medrxiv landing -> no citation_pdf_url meta tag")
            continue
        pdf_url = pdf_m.group(1)
        time.sleep(1.0)
        status, pdf_body, _ = _http_get(pdf_url, timeout=60)
        if status != 200 or not pdf_body:
            log.append(f"tried: biorxiv/medrxiv PDF ({pdf_url}) -> HTTP {status}")
            continue
        extracted = pdf_to_text(pdf_body)
        meta = {
            "title": title_m.group(1) if title_m else None,
            "year": int(year_m.group(1)) if year_m else None,
            "source_url": pdf_url,
        }
        if extracted and len(extracted) > 500:
            log.append(
                f"tried: biorxiv/medrxiv + pdftotext -> success ({len(pdf_body)} bytes -> {len(extracted)} chars)"
            )
            return extracted, meta
        log.append(
            f"tried: biorxiv/medrxiv -> got PDF ({len(pdf_body)} bytes) but "
            f"{'pdftotext not installed' if not extracted else 'extraction too short'}"
        )
        return f"[PDF body fetched from {pdf_url}, {len(pdf_body)} bytes — install pdftotext to extract]", meta
    return None, {}


def fetch_openreview(openreview_id_or_url: str, log: list[str]) -> tuple[str | None, dict]:
    """Rung for openreview.net papers (NeurIPS / ICML / ICLR / CoLLAs / etc.).

    Extract the id from the URL if needed, then directly fetch the PDF from
    https://openreview.net/pdf?id=<id> and parse with pdftotext.
    """
    m = re.search(r"[?&]id=([A-Za-z0-9_-]+)", openreview_id_or_url)
    paper_id = m.group(1) if m else openreview_id_or_url
    pdf_url = f"https://openreview.net/pdf?id={paper_id}"
    time.sleep(2.0)
    status, pdf_body, _ = _http_get(pdf_url, timeout=60)
    if status != 200 or not pdf_body:
        log.append(f"tried: openreview PDF ({pdf_url}) -> HTTP {status}")
        return None, {"source_url": pdf_url}
    extracted = pdf_to_text(pdf_body)
    meta = {"source_url": pdf_url}
    if extracted and len(extracted) > 500:
        log.append(
            f"tried: openreview + pdftotext -> success ({len(pdf_body)} bytes -> {len(extracted)} chars)"
        )
        return extracted, meta
    log.append(
        f"tried: openreview -> got PDF ({len(pdf_body)} bytes) but "
        f"{'pdftotext not installed' if not extracted else 'extraction too short'}"
    )
    return f"[PDF body fetched from {pdf_url}, {len(pdf_body)} bytes — install pdftotext to extract]", meta


def fetch_scihub(doi: str, log: list[str]) -> tuple[str | None, dict]:
    """Opt-in rung. Fires ONLY when SCI_HUB_MIRROR env var is set.

    Legal/ethical tradeoff is documented at the top of this file. Default behavior
    is "disabled" — the env var must be explicitly set by the user. Every call
    appends a clear line to fetch_log so there is no silent activation.
    """
    if not SCI_HUB_MIRROR:
        # Don't even log when the env var is unset — the rung simply doesn't exist.
        return None, {}

    url = f"{SCI_HUB_MIRROR}/{urllib.parse.quote(doi, safe='/:')}"
    time.sleep(2.0)
    status, body, _ = _http_get(url, timeout=45, accept="text/html")
    if status != 200 or not body:
        log.append(f"tried: sci-hub via {SCI_HUB_MIRROR} -> HTTP {status}")
        return None, {}
    html = body.decode("utf-8", errors="replace")

    # Sci-Hub's typical layout embeds the PDF URL in <embed src="..."> or <iframe src="...">.
    # The URL often lacks a scheme (starts with `//`) or is a site-relative /path.
    embed_m = re.search(r'<(?:embed|iframe)[^>]+src="([^"]+)"', html)
    if not embed_m:
        log.append(f"tried: sci-hub via {SCI_HUB_MIRROR} -> landing page had no embed/iframe")
        return None, {}
    pdf_url = embed_m.group(1).split("#")[0]
    if pdf_url.startswith("//"):
        pdf_url = "https:" + pdf_url
    elif pdf_url.startswith("/"):
        pdf_url = SCI_HUB_MIRROR + pdf_url

    time.sleep(2.0)
    status, pdf_body, _ = _http_get(pdf_url, timeout=60)
    if status != 200 or not pdf_body:
        log.append(f"tried: sci-hub PDF ({pdf_url}) -> HTTP {status}")
        return None, {}
    extracted = pdf_to_text(pdf_body)
    meta = {"source_url": pdf_url}
    if extracted and len(extracted) > 500:
        log.append(
            f"tried: sci-hub via {SCI_HUB_MIRROR} + pdftotext -> success "
            f"({len(pdf_body)} bytes -> {len(extracted)} chars) [OPT-IN rung]"
        )
        return extracted, meta
    log.append(
        f"tried: sci-hub via {SCI_HUB_MIRROR} -> got PDF ({len(pdf_body)} bytes) but "
        f"{'pdftotext not installed' if not extracted else 'extraction too short'} [OPT-IN rung]"
    )
    return f"[PDF body fetched from Sci-Hub, {len(pdf_body)} bytes — install pdftotext to extract]", meta


def fetch_arxiv_abstract(arxiv_id: str, log: list[str]) -> tuple[str | None, dict]:
    url = f"https://arxiv.org/abs/{arxiv_id}"
    time.sleep(3.0)
    status, body, _ = _http_get(url, timeout=30, accept="text/html")
    if status != 200:
        log.append(f"tried: arxiv abs page -> HTTP {status}")
        return None, {}
    html = body.decode("utf-8", errors="replace")
    # citation_abstract meta tag is the cleanest source for the abstract
    m = re.search(r'<meta name="citation_abstract" content="([^"]+)"', html)
    abstract = m.group(1) if m else None
    title_m = re.search(r'<meta name="citation_title" content="([^"]+)"', html)
    title = title_m.group(1) if title_m else None
    authors = re.findall(r'<meta name="citation_author" content="([^"]+)"', html)
    year_m = re.search(r'<meta name="citation_date" content="([0-9]{4})', html)
    year = int(year_m.group(1)) if year_m else None
    if abstract:
        log.append(f"tried: arxiv abs page -> abstract recovered ({len(abstract)} chars)")
        return abstract, {"title": title, "authors": authors, "year": year}
    log.append("tried: arxiv abs page -> no abstract meta tag")
    return None, {"title": title, "authors": authors, "year": year}


# ----------------------------- main ladder ------------------------------------


def fetch_by_arxiv(arxiv_id: str) -> dict:
    log: list[str] = []
    paper_id = f"arxiv:{arxiv_id}"

    cached = _read_cache(paper_id)
    if cached:
        return {"_cached": True, "paper_id": paper_id, "_cached_text": cached["_cached_text"]}

    text = fetch_arxiv_source(arxiv_id, log)
    if text:
        return {
            "paper_id": paper_id,
            "source_url": f"https://arxiv.org/e-print/{arxiv_id}",
            "retrieval_quality": "full-text",
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
        }

    text = fetch_ar5iv(arxiv_id, log)
    if text:
        return {
            "paper_id": paper_id,
            "source_url": f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}",
            "retrieval_quality": "full-text-no-refs",
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
        }

    abstract, meta = fetch_arxiv_abstract(arxiv_id, log)
    if abstract:
        return {
            "paper_id": paper_id,
            "title": meta.get("title"),
            "authors": meta.get("authors") or [],
            "year": meta.get("year"),
            "source_url": f"https://arxiv.org/abs/{arxiv_id}",
            "retrieval_quality": "abstract-only",
            "text": abstract,
            "fetch_log": log,
            "cache_hit": False,
        }

    return {
        "paper_id": paper_id,
        "retrieval_quality": "unreachable",
        "text": "",
        "fetch_log": log,
        "cache_hit": False,
        "notes": "All ladder rungs failed; paper could not be retrieved.",
    }


def _is_full_text(text: str | None) -> bool:
    """Heuristic: a returned text is full-text if it's long and isn't the bytes-marker."""
    return bool(text) and len(text) > 500 and not text.startswith("[PDF body fetched")


def fetch_by_doi(doi: str) -> dict:
    log: list[str] = []
    paper_id = f"doi:{doi}"

    cached = _read_cache(paper_id)
    if cached:
        return {"_cached": True, "paper_id": paper_id, "_cached_text": cached["_cached_text"]}

    # biorxiv / medrxiv — try first when DOI prefix matches, since they're cleaner
    # than OpenAlex for biology preprints.
    if doi.startswith("10.1101/"):
        text, meta = fetch_biorxiv(doi, log)
        if text:
            quality = "full-text" if _is_full_text(text) else "body-partial"
            return {
                "paper_id": paper_id,
                "title": meta.get("title"),
                "year": meta.get("year"),
                "source_url": meta.get("source_url", ""),
                "retrieval_quality": quality,
                "text": text,
                "fetch_log": log,
                "cache_hit": False,
            }

    text, meta = fetch_openalex_oa(doi, log)
    if text:
        quality = "full-text" if _is_full_text(text) else "body-partial"
        return {
            "paper_id": paper_id,
            "title": (meta.get("title") or ""),
            "year": meta.get("publication_year"),
            "venue": ((meta.get("host_venue") or {}).get("display_name") or ""),
            "source_url": (meta.get("open_access") or {}).get("oa_url", ""),
            "retrieval_quality": quality,
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
        }

    text, meta = fetch_unpaywall(doi, log)
    if text:
        quality = "full-text" if _is_full_text(text) else "body-partial"
        return {
            "paper_id": paper_id,
            "source_url": (meta.get("best_oa_location") or {}).get("url_for_pdf", ""),
            "retrieval_quality": quality,
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
        }

    # Sci-Hub — opt-in rung, fires ONLY when SCI_HUB_MIRROR env var is set.
    text, meta = fetch_scihub(doi, log)
    if text:
        quality = "full-text" if _is_full_text(text) else "body-partial"
        return {
            "paper_id": paper_id,
            "source_url": meta.get("source_url", ""),
            "retrieval_quality": quality,
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
            "notes": "Fetched via user-enabled Sci-Hub rung (SCI_HUB_MIRROR set).",
        }

    return {
        "paper_id": paper_id,
        "retrieval_quality": "unreachable",
        "text": "",
        "fetch_log": log,
        "cache_hit": False,
        "notes": (
            "DOI is closed-access (no OA copy via OpenAlex or Unpaywall). "
            "Set SCI_HUB_MIRROR env var to enable the opt-in Sci-Hub rung if acceptable "
            "for your jurisdiction/use case."
        ),
    }


def fetch_by_openreview(openreview_ref: str) -> dict:
    """Dispatch entry point for openreview URLs / IDs."""
    log: list[str] = []
    paper_id = f"openreview:{re.sub(r'[^A-Za-z0-9_-]+', '', openreview_ref)[:64]}"

    cached = _read_cache(paper_id)
    if cached:
        return {"_cached": True, "paper_id": paper_id, "_cached_text": cached["_cached_text"]}

    text, meta = fetch_openreview(openreview_ref, log)
    if text:
        quality = "full-text" if _is_full_text(text) else "body-partial"
        return {
            "paper_id": paper_id,
            "source_url": meta.get("source_url", ""),
            "retrieval_quality": quality,
            "text": text,
            "fetch_log": log,
            "cache_hit": False,
        }
    return {
        "paper_id": paper_id,
        "retrieval_quality": "unreachable",
        "text": "",
        "fetch_log": log,
        "cache_hit": False,
        "notes": "OpenReview PDF could not be retrieved (ID may be wrong, or paper is private).",
    }


# ----------------------------- entry point ------------------------------------


def classify_url(url: str) -> tuple[str, str] | None:
    """Return (kind, id_or_ref) for a paper URL we know how to dispatch, else None.

    kind ∈ {"arxiv", "biorxiv", "medrxiv", "openreview"}
    """
    m = re.search(r"arxiv\.org/(?:abs|pdf|html|e-print)/([0-9]{4}\.[0-9]{4,5})", url)
    if m:
        return "arxiv", m.group(1)
    if "biorxiv.org" in url or "medrxiv.org" in url:
        # Extract the DOI (10.1101/...) from the URL path if present
        doi_m = re.search(r"(10\.1101/[\w.\-]+)", url)
        return ("biorxiv" if "biorxiv.org" in url else "medrxiv"), (doi_m.group(1) if doi_m else url)
    if "openreview.net" in url:
        return "openreview", url
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch a paper's full text via the retrieval ladder.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--arxiv-id", help="arXiv id, e.g. 2403.12345")
    g.add_argument("--doi", help="DOI, e.g. 10.1145/3580305.3599489 (biorxiv/medrxiv DOIs auto-routed)")
    g.add_argument("--openreview-id", help="OpenReview paper id, e.g. abc123XYZ")
    g.add_argument("--url", help="Paper URL (arxiv, biorxiv, medrxiv, openreview auto-detected)")
    args = parser.parse_args()

    if args.arxiv_id:
        result = fetch_by_arxiv(args.arxiv_id)
    elif args.doi:
        result = fetch_by_doi(args.doi)
    elif args.openreview_id:
        result = fetch_by_openreview(args.openreview_id)
    else:
        url = args.url
        classified = classify_url(url)
        if classified:
            kind, ref = classified
            if kind == "arxiv":
                result = fetch_by_arxiv(ref)
            elif kind in {"biorxiv", "medrxiv"}:
                # biorxiv/medrxiv DOIs share the 10.1101/ prefix; fetch_by_doi auto-routes.
                result = fetch_by_doi(ref) if ref.startswith("10.1101/") else {
                    "paper_id": f"{kind}:{ref}",
                    "retrieval_quality": "unreachable",
                    "text": "",
                    "fetch_log": [f"could not extract 10.1101/ DOI from {ref}"],
                    "cache_hit": False,
                }
            elif kind == "openreview":
                result = fetch_by_openreview(ref)
            else:
                print(f"# unsupported URL kind: {kind}", file=sys.stderr)
                return 2
        else:
            print(f"# unsupported URL: {url}", file=sys.stderr)
            print("# supported: arxiv, biorxiv, medrxiv, openreview — or pass --doi for DOIs", file=sys.stderr)
            return 2

    if "_cached" in result:
        # Serve from cache verbatim.
        sys.stdout.write(result["_cached_text"])
        return 0

    yaml_text = _yaml_dump(result)
    _write_cache(result["paper_id"], yaml_text)
    sys.stdout.write(yaml_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
