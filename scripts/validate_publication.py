"""Validate a rendered lesson publication candidate and report release blockers."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess

import yaml

from scripts.validate_package import ROOT, validate_lesson_package


BLOCKED_TEXT = re.compile(r"\b(?:TODO|TBD|placeholder)\b", re.IGNORECASE)
PRIVATE_MARKERS = re.compile(r"\bS\d{3,}\b|display_name|private/students", re.IGNORECASE)


def validate_publication(package: Path) -> tuple[list[str], list[str]]:
    blockers = validate_lesson_package(package)
    warnings: list[str] = []
    manifest_path = package / "publication.yaml"
    if not manifest_path.is_file():
        return blockers + ["publication manifest is missing"], warnings
    publication = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))["publication"]
    if publication.get("package_id") != yaml.safe_load((package / "lesson.yaml").read_text(encoding="utf-8"))["lesson"]["id"]:
        blockers.append("publication package id differs from lesson id")

    for name in publication.get("source_artifacts", []):
        path = package / name
        if not path.is_file():
            blockers.append(f"source artifact missing: {name}")
            continue
        if path.suffix in {".md", ".yaml", ".json"}:
            text = path.read_text(encoding="utf-8")
            if BLOCKED_TEXT.search(text):
                blockers.append(f"draft marker found in {name}")
            if PRIVATE_MARKERS.search(text):
                blockers.append(f"possible private learner marker found in {name}")

    candidate_root = ROOT / publication["candidate_root"]
    for name in publication.get("rendered_artifacts", []):
        path = candidate_root / name
        if not path.is_file() or path.stat().st_size < 500:
            blockers.append(f"rendered artifact missing or empty: {name}")
        elif path.suffix == ".pdf" and path.read_bytes()[:4] != b"%PDF":
            blockers.append(f"rendered artifact is not a PDF: {name}")
        elif path.suffix == ".pdf":
            info = subprocess.run(["pdfinfo", str(path)], text=True, capture_output=True)
            pages = re.search(r"^Pages:\s+(\d+)$", info.stdout, re.MULTILINE)
            if info.returncode or not pages or int(pages.group(1)) < 1:
                blockers.append(f"rendered PDF has no verifiable pages: {name}")
            if name == "slides.pdf" and (not pages or int(pages.group(1)) < 10):
                blockers.append("rendered slide PDF is incomplete")
            if name == "slides.pdf":
                tagged = re.search(r"^Tagged:\s+yes$", info.stdout, re.MULTILINE | re.IGNORECASE)
                if publication.get("status") == "publication-ready" and not tagged:
                    blockers.append("publication-ready slide PDF must be tagged for accessibility")
        elif path.suffix == ".html":
            text = path.read_text(encoding="utf-8")
            if '<html lang="en">' not in text or '<meta name="viewport"' not in text:
                blockers.append(f"HTML accessibility metadata missing: {name}")

    quarto_source = package / "slides.qmd"
    if quarto_source.is_file():
        source = quarto_source.read_text(encoding="utf-8")
        slide_ids = re.findall(r"^## .+?\{#([a-z0-9-]+)\}\s*$", source, re.MULTILINE)
        note_blocks = re.findall(r"^::: \{\.notes\}\s*$", source, re.MULTILINE)
        visuals = re.findall(r"!\[\]\(assets/[^)]+\.svg\)\{[^}]*fig-alt=", source)
        if not slide_ids or len(slide_ids) != len(note_blocks):
            blockers.append("every instructional slide must have a stable id and speaker notes")
        if len(visuals) < 6:
            blockers.append("deck does not meet the explanatory-visual minimum")
    lesson_status = yaml.safe_load((package / "lesson.yaml").read_text(encoding="utf-8"))["lesson"].get("status")
    if publication.get("status") not in {"publication-candidate", "publication-ready"}:
        blockers.append("publication manifest has an invalid release status")
    if lesson_status != publication.get("status"):
        blockers.append("lesson and publication release statuses differ")
    if publication.get("status") == "publication-ready":
        if not publication.get("validated_on"):
            blockers.append("publication-ready package has no validation date")
        failed = [name for name, result in publication.get("release_checks", {}).items() if result != "passed"]
        if failed:
            blockers.append("publication-ready package has incomplete release checks")
    formats = publication.get("format_accessibility", {})
    if formats.get("slides_html") != "primary-accessible-format":
        blockers.append("publication manifest must identify the primary accessible slide format")
    if formats.get("slides_pdf") not in {"tagged-accessible", "print-reference-untagged"}:
        blockers.append("publication manifest must declare slide PDF accessibility")
    return blockers, warnings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args(argv)
    blockers, warnings = validate_publication(args.package)
    for warning in warnings:
        print(f"WARNING: {warning}")
    for blocker in blockers:
        print(f"BLOCKER: {blocker}")
    if blockers:
        return 1
    print(f"Publication candidate passed with {len(warnings)} warning(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
