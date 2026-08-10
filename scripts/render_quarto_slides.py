"""Render a Quarto Reveal deck and fail on accessibility or PDF integrity errors."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

import yaml


ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN = yaml.safe_load((ROOT / "config" / "toolchain.yaml").read_text(encoding="utf-8"))["presentation_toolchain"]
QUARTO = ROOT / TOOLCHAIN["quarto"]["install_path"] / "bin" / "quarto"
NODE = ROOT / TOOLCHAIN["node"]["install_path"] / "bin" / "node"
DECKTAPE = ROOT / "node_modules" / "decktape" / "decktape.js"
CHROME = TOOLCHAIN["decktape"]["browser"]


def run(command: list[str]) -> str:
    process = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    output = process.stdout + process.stderr
    if process.returncode:
        raise RuntimeError(output)
    return output


def render(package: Path, output: Path) -> tuple[Path, Path]:
    source = package / "slides.qmd"
    for executable in [QUARTO, NODE]:
        if not executable.is_file():
            raise RuntimeError(f"tool missing: {executable}; run the matching bootstrap script")
    if not DECKTAPE.is_file():
        raise RuntimeError("DeckTape missing; run PUPPETEER_SKIP_DOWNLOAD=true npm install --ignore-scripts")

    output.mkdir(parents=True, exist_ok=True)
    run([str(QUARTO), "render", str(source), "--to", "revealjs", "--output-dir", str(output)])
    html = output / "slides.html"
    pdf = output / "slides.pdf"
    decktape_output = run([
        str(NODE), str(DECKTAPE), "reveal",
        "--chrome-path", CHROME,
        "--size", "1600x900",
        html.resolve().as_uri(), str(pdf.resolve()),
    ])
    violations = [line for line in decktape_output.splitlines() if line.startswith("Ensure ")]
    if violations:
        raise RuntimeError("Accessibility violations:\n" + "\n".join(violations))

    info = run(["pdfinfo", str(pdf)])
    pages_match = re.search(r"^Pages:\s+(\d+)$", info, re.MULTILINE)
    expected_pages = 1 + sum(1 for line in source.read_text(encoding="utf-8").splitlines() if line.startswith("## "))
    if not pages_match or int(pages_match.group(1)) != expected_pages:
        raise RuntimeError(f"PDF page count does not match deck: expected {expected_pages}")
    return html, pdf


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    output = args.output or ROOT / "outputs" / "publication-candidates" / args.package.parent.name / args.package.name
    html, pdf = render(args.package, output)
    print(f"Rendered accessible HTML deck and print-reference PDF: {html} and {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
