"""Render and validate every lesson publication candidate from source."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.render_documents import DOCUMENTS, ROOT, render_document
from scripts.render_quarto_slides import render as render_slides
from scripts.validate_publication import validate_publication


def candidate_packages() -> list[Path]:
    return sorted(path.parent for path in (ROOT / "content" / "lessons").glob("unit-*/competency-*/publication.yaml"))


def build(package: Path) -> Path:
    destination = ROOT / "outputs" / "publication-candidates" / package.parent.name / package.name
    for name in DOCUMENTS:
        source = package / name
        render_document(source, destination / f"{source.stem}.html", destination / f"{source.stem}.pdf")
    render_slides(package, destination)
    blockers, warnings = validate_publication(package)
    for warning in warnings:
        print(f"WARNING: {package}: {warning}")
    if blockers:
        details = "\n".join(f"- {blocker}" for blocker in blockers)
        raise RuntimeError(f"publication validation failed for {package}:\n{details}")
    print(f"Built and validated {package} -> {destination}")
    return destination


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", nargs="*", type=Path, help="lesson package directories; defaults to every package with publication.yaml")
    args = parser.parse_args(argv)
    packages = args.packages or candidate_packages()
    if not packages:
        parser.error("no publication candidates found")
    for package in packages:
        build(package)
    print(f"Built {len(packages)} publication candidate(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
