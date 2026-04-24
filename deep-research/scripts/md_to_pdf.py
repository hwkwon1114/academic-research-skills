#!/usr/bin/env python3
"""Convert a Markdown lit-review report to PDF via pandoc (primary) or weasyprint (optional).

Usage:
    python3 md_to_pdf.py --input report.md [--output report.pdf] [--engine pandoc|weasyprint]

Exit codes:
    0  Success
    1  Input file error or argument error
    2  Engine not found / conversion failed
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert Markdown to PDF. Requires pandoc (default) or weasyprint."
    )
    parser.add_argument("--input", required=True, help="Path to the input .md file")
    parser.add_argument("--output", help="Path for the output .pdf file (default: same dir, .pdf extension)")
    parser.add_argument(
        "--engine",
        choices=["pandoc", "weasyprint"],
        default="pandoc",
        help="PDF engine to use (default: pandoc)",
    )
    return parser.parse_args()


def _missing_engine_message(engine: str, input_path: str) -> str:
    if engine == "pandoc":
        return (
            f"ERROR: pandoc not found. "
            f"Install via 'brew install pandoc' (macOS) or 'apt install pandoc' (Linux). "
            f"Markdown unchanged at {input_path}."
        )
    return (
        f"ERROR: weasyprint not found. "
        f"Install via 'pip install weasyprint'. "
        f"Markdown unchanged at {input_path}."
    )


def convert_pandoc(input_path: Path, output_path: Path) -> int:
    if not shutil.which("pandoc"):
        print(_missing_engine_message("pandoc", str(input_path)), file=sys.stderr)
        return 2
    cmd = [
        "pandoc",
        str(input_path),
        "-o",
        str(output_path),
        "--standalone",
        "--pdf-engine=xelatex",
    ]
    # Fallback to pdflatex if xelatex not available
    if not shutil.which("xelatex"):
        cmd = [
            "pandoc",
            str(input_path),
            "-o",
            str(output_path),
            "--standalone",
        ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"ERROR: pandoc conversion failed.\n{result.stderr}", file=sys.stderr)
        return 2
    return 0


def convert_weasyprint(input_path: Path, output_path: Path) -> int:
    try:
        import weasyprint  # lazy import — optional third-party dependency
    except ImportError:
        print(_missing_engine_message("weasyprint", str(input_path)), file=sys.stderr)
        return 2
    try:
        import markdown as md_lib  # also optional
    except ImportError:
        print(
            "ERROR: 'markdown' package not found. Install via 'pip install markdown'. "
            f"Markdown unchanged at {input_path}.",
            file=sys.stderr,
        )
        return 2
    html = md_lib.markdown(input_path.read_text(encoding="utf-8"), extensions=["tables", "fenced_code"])
    try:
        weasyprint.HTML(string=html).write_pdf(str(output_path))
    except Exception as exc:
        print(f"ERROR: weasyprint conversion failed: {exc}", file=sys.stderr)
        return 2
    return 0


def main() -> int:
    args = parse_args()
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: input file not found: {input_path}", file=sys.stderr)
        return 1
    if input_path.suffix.lower() != ".md":
        print(f"ERROR: input file must be a .md file: {input_path}", file=sys.stderr)
        return 1

    output_path = Path(args.output) if args.output else input_path.with_suffix(".pdf")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if args.engine == "pandoc":
        return convert_pandoc(input_path, output_path)
    else:
        return convert_weasyprint(input_path, output_path)


if __name__ == "__main__":
    sys.exit(main())
