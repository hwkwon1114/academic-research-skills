#!/usr/bin/env python3
"""
slugify.py — turn a free-form noun phrase into a vault-safe wikilink slug.

Used by the deep-research vault profile (synthesize / paper-review modes) so the
free-form `target_concept:` strings emitted by bibliography_agent become
deterministic `[[wikilinks]]` in the report compiler's output.

Rules:
  - Lowercase
  - Drop English articles (the, a, an) and possessive 's
  - Replace any non-alphanumeric run with a single hyphen
  - Collapse multiple hyphens; strip leading/trailing hyphens
  - ASCII-only (transliterate via NFKD where possible)

Examples:
  "Gaussian Process method"           -> "gaussian-process-method"
  "GP smoothness assumption"          -> "gp-smoothness-assumption"
  "sim-to-real gap"                   -> "sim-to-real-gap"
  "the Lorenz system's attractor"     -> "lorenz-system-attractor"
  "DeepONet"                          -> "deeponet"
  "Convergent Cross-Mapping (CCM)"    -> "convergent-cross-mapping-ccm"

Usage:
  python slugify.py "Gaussian Process method"
  echo "GP smoothness assumption" | python slugify.py -
"""
from __future__ import annotations

import re
import sys
import unicodedata

ARTICLES = {"the", "a", "an"}


def slugify(phrase: str) -> str:
    """Convert a noun phrase to a kebab-case slug, dropping English articles."""
    # Transliterate to ASCII via NFKD decomposition, drop combining marks.
    normalized = unicodedata.normalize("NFKD", phrase)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")

    # Drop possessive 's before tokenizing, so "Lorenz system's" -> "Lorenz system".
    ascii_only = re.sub(r"'s\b", "", ascii_only)

    # Tokenize on non-alphanumeric runs.
    tokens = [t for t in re.split(r"[^A-Za-z0-9]+", ascii_only) if t]

    # Lowercase and drop articles.
    tokens = [t.lower() for t in tokens if t.lower() not in ARTICLES]

    if not tokens:
        return ""
    return "-".join(tokens)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: slugify.py <phrase> | -", file=sys.stderr)
        return 2
    arg = sys.argv[1]
    phrase = sys.stdin.read().strip() if arg == "-" else arg
    print(slugify(phrase))
    return 0


if __name__ == "__main__":
    sys.exit(main())
