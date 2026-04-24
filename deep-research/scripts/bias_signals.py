#!/usr/bin/env python3
"""
bias_signals.py — structural-indicator gatherer for ml_comparison_bias_agent.

This is NOT a replacement for the agent's judgment — it's a signal gatherer.
Given a paper's body text (from paper_fetch.py's full-text output), it
greps for structural patterns that correlate with the 5 bias checks the agent
performs, and returns a report of what's present / absent. The agent then
reads the report plus the paper body and renders the actual bias verdict.

The value: every invocation uses the same regex patterns, so the signals are
comparable across papers. An agent that's "too generous" on variance reporting
in paper A but "too strict" on paper B is a known drift mode; grounding both
on the same regex output reduces that drift.

Usage:
  # From a paper text file:
  python3 bias_signals.py --paper-path paper-body.md

  # From stdin (pipe from paper_fetch.py):
  python3 paper_fetch.py --arxiv-id 2010.08895 | python3 bias_signals.py -

Output: JSON report with one entry per bias-signal family, each carrying
`found: bool`, `matches_count: int`, and up to 5 example snippets.

Signals (mapped to the agent's 5 checks):
  1. Variance reporting      → supports metric bias + data leakage assessment
  2. Hyperparameter search   → supports hyperparameter fairness
  3. Compute budget          → supports compute-budget asymmetry
  4. Baseline enumeration    → supports benchmark selection
  5. Code/data availability  → supports reproducibility
  6. Multi-seed / bootstrap  → supports metric bias
  7. Ablation                → supports hyperparameter fairness + metric bias
  8. Single-benchmark warn   → flag for benchmark-selection bias
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


# Each pattern has: a human-readable name, a regex, and a short rationale
# the agent can surface as part of its verdict. Case-insensitive.
PATTERNS = [
    (
        "variance_reporting",
        r"(?i)(?:\b(?:std\.?\s*dev|standard\s+deviation|variance|\bstd\b|error\s+bars?|confidence\s+interval|95%\s*CI)\b|±|\+/-)",
        "Does the paper report spread around its mean metrics?",
    ),
    (
        "hyperparameter_search",
        r"(?i)\b(?:grid\s+search|random\s+search|hyperparameter\s+(?:search|tuning|sweep|optimization)|bayesian\s+optimization|HPO)\b",
        "Does the paper describe a hyperparameter-selection procedure?",
    ),
    (
        "compute_budget",
        r"(?i)\b(?:GPU-?\s*hours?|TPU-?\s*hours?|wall[-\s]?clock|training\s+time|compute\s+budget|FLOPs?|PetaFLOPs?|TeraFLOPs?)\b",
        "Does the paper disclose compute budget / training time?",
    ),
    (
        "multi_seed",
        r"(?i)\b(?:(?:multiple|[3-9]|10)\s+(?:random\s+)?seeds?|bootstrap(?:ped)?|mean\s+of\s+(?:[3-9]|10)\s+runs)\b",
        "Does the paper average over multiple seeds / bootstrap runs?",
    ),
    (
        "ablation",
        r"(?i)\bablation(?:s?|\s+study|\s+results?)\b",
        "Does the paper include an ablation study?",
    ),
    (
        "code_release",
        r"(?i)(?:github\.com|gitlab\.com|code\s+(?:is\s+)?(?:available|released)|open[-\s]?sourced?|publicly\s+available\s+code|anonymous\.4open\.science)",
        "Is code publicly released?",
    ),
    (
        "data_release",
        r"(?i)(?:dataset\s+(?:is\s+)?(?:available|released|public)|data\s+(?:is\s+)?publicly\s+(?:available|released))",
        "Is the dataset publicly released?",
    ),
    (
        "baseline_enumeration",
        r"(?i)\b(?:baseline(?:s)?|compared\s+(?:against|to|with)|outperforms?|benchmark(?:s|ing)?)\b",
        "How extensively does the paper reference baselines / benchmarks?",
    ),
    (
        "single_benchmark_warning",
        r"(?i)\b(?:on\s+(?:a|the|one|our)\s+(?:new\s+)?benchmark|single\s+benchmark|bespoke\s+benchmark|custom\s+benchmark)\b",
        "Flag for single-or-custom-benchmark evaluation (benchmark-selection bias indicator).",
    ),
    (
        "fairness_disclaimer",
        r"(?i)\bhyperparameters\s+(?:were\s+)?(?:chosen|tuned|set)\s+(?:equally|fairly|identically)\b",
        "Does the paper explicitly claim hyperparameter-budget parity across methods?",
    ),
    (
        "leakage_flag",
        r"(?i)\b(?:train/test\s+split|data\s+leakage|test\s+set\s+(?:contamination|leak|overlap)|test\s+examples?\s+(?:may|might)\s+appear)\b",
        "Does the paper discuss data-leakage risk?",
    ),
]


def scan_text(text: str) -> dict:
    report: dict = {"signals": {}}
    # Normalize whitespace so regex matches span line breaks from wrapped TeX/markdown.
    normalized = re.sub(r"\s+", " ", text)
    for name, pattern, rationale in PATTERNS:
        matches = list(re.finditer(pattern, normalized))
        snippets: list[str] = []
        for m in matches[:5]:
            start = max(0, m.start() - 60)
            end = min(len(normalized), m.end() + 60)
            snippet = normalized[start:end].strip()
            snippets.append("…" + snippet + "…")
        report["signals"][name] = {
            "found": len(matches) > 0,
            "matches_count": len(matches),
            "snippets": snippets,
            "rationale": rationale,
        }

    # Aggregate assessment suggestions — NOT verdicts, just hints.
    s = report["signals"]
    report["aggregate_hints"] = {
        "likely_fair_hyperparameter_budget": s["fairness_disclaimer"]["found"] and s["hyperparameter_search"]["found"],
        "has_variance_evidence": s["variance_reporting"]["found"] or s["multi_seed"]["found"],
        "compute_disclosed": s["compute_budget"]["found"],
        "reproducibility_artifacts": s["code_release"]["found"] or s["data_release"]["found"],
        "single_benchmark_risk": s["single_benchmark_warning"]["found"] and s["baseline_enumeration"]["matches_count"] < 3,
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Bias-signal gatherer for ml_comparison_bias_agent.")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--paper-path", help="path to a markdown/text file with the paper body")
    g.add_argument("stdin", nargs="?", help="pass '-' to read paper body from stdin")
    args = parser.parse_args()

    if args.paper_path:
        text = Path(args.paper_path).read_text()
    else:
        text = sys.stdin.read()

    report = scan_text(text)
    json.dump(report, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
