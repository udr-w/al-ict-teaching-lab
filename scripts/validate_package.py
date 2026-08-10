"""Validate teaching packages before review or publication."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = {
    "lesson.yaml",
    "teacher-notes.md",
    "slides.md",
    "worksheet.md",
    "practical.md",
    "homework.md",
    "answers.md",
    "provenance.json",
}
ASSESSMENT_FILES = {
    "assessment.yaml",
    "blueprint.yaml",
    "paper.md",
    "marking-scheme.md",
    "provenance.json",
}


def validate_lesson_package(package: Path) -> list[str]:
    errors: list[str] = []
    missing = sorted(name for name in REQUIRED_FILES if not (package / name).is_file())
    if missing:
        return [f"missing required file: {name}" for name in missing]

    lesson = yaml.safe_load((package / "lesson.yaml").read_text(encoding="utf-8"))["lesson"]
    unit_paths = sorted((ROOT / "curriculum" / "units").glob("*.yaml"))
    curriculum_levels = {
        level["id"]: level
        for path in unit_paths
        for level in yaml.safe_load(path.read_text(encoding="utf-8"))["unit"]["competency_levels"]
    }
    curriculum_level = curriculum_levels.get(lesson.get("competency"))
    if curriculum_level is None:
        errors.append("lesson competency is absent from the curriculum model")
    else:
        if lesson.get("allocated_periods") != curriculum_level.get("periods"):
            errors.append("lesson period allocation differs from the curriculum model")
        if lesson.get("curriculum_source", {}).get("printed_page") not in curriculum_level.get("source_printed_pages", []):
            errors.append("lesson source page differs from the curriculum model")
    unknown_prerequisites = set(lesson.get("prerequisites", [])) - set(curriculum_levels)
    if unknown_prerequisites:
        errors.append("lesson references an unknown prerequisite")
    outcomes = lesson.get("learning_outcomes", [])
    if not outcomes or any(not item.get("id") or not item.get("statement") for item in outcomes):
        errors.append("lesson must define identified learning outcomes")
    if lesson.get("allocated_periods", 0) <= 0:
        errors.append("lesson must define a positive period allocation")

    sequence = lesson.get("sequence", [])
    if len(sequence) != lesson.get("allocated_periods"):
        errors.append("sequence length must equal allocated periods")
    known_outcomes = {item["id"] for item in outcomes}
    used_outcomes = {item for session in sequence for item in session.get("outcomes", [])}
    if used_outcomes != known_outcomes:
        errors.append("sequence must cover every learning outcome and no unknown outcomes")

    provenance = json.loads((package / "provenance.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "sources" / "manifest.yaml").read_text(encoding="utf-8"))
    registered = {source["id"] for source in manifest["sources"]}
    claims = provenance.get("curriculum_claims", [])
    if not claims:
        errors.append("provenance must contain curriculum claims")
    for claim in claims:
        if claim.get("source_id") not in registered:
            errors.append("provenance references an unregistered source")
        if not claim.get("printed_pages"):
            errors.append("curriculum claim must include printed pages")

    for name in REQUIRED_FILES - {"lesson.yaml", "provenance.json"}:
        meaningful = [
            line for line in (package / name).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if not meaningful:
            errors.append(f"{name} contains no substantive content")
    return errors


def validate_assessment_package(package: Path) -> list[str]:
    errors: list[str] = []
    missing = sorted(name for name in ASSESSMENT_FILES if not (package / name).is_file())
    if missing:
        return [f"missing required file: {name}" for name in missing]

    assessment = yaml.safe_load((package / "assessment.yaml").read_text(encoding="utf-8"))["assessment"]
    blueprint = yaml.safe_load((package / "blueprint.yaml").read_text(encoding="utf-8"))["blueprint"]
    questions = blueprint.get("questions", [])
    if blueprint.get("assessment_id") != assessment.get("id"):
        errors.append("blueprint assessment id does not match assessment")
    if sum(question.get("marks", 0) for question in questions) != assessment.get("total_marks"):
        errors.append("blueprint question marks do not equal assessment total")

    competency_totals: dict[str, int] = {}
    cognitive_totals: dict[str, int] = {}
    for question in questions:
        competency_totals[question["competency"]] = competency_totals.get(question["competency"], 0) + question["marks"]
        demand = question["cognitive_demand"]
        cognitive_totals[demand] = cognitive_totals.get(demand, 0) + question["marks"]
        if not question.get("outcomes") or not question.get("command_words"):
            errors.append(f"{question.get('id', 'question')} lacks alignment metadata")
    if competency_totals != blueprint.get("competency_mark_totals"):
        errors.append("declared competency mark totals are inconsistent")
    if cognitive_totals != blueprint.get("cognitive_mark_totals"):
        errors.append("declared cognitive mark totals are inconsistent")
    if set(competency_totals) != set(assessment.get("competencies", [])):
        errors.append("blueprint does not cover the declared competencies")

    paper = (package / "paper.md").read_text(encoding="utf-8")
    scheme = (package / "marking-scheme.md").read_text(encoding="utf-8")
    for question in questions:
        heading = f"## {question['id']}"
        if heading not in paper or heading not in scheme:
            errors.append(f"{question['id']} is missing from paper or marking scheme")

    provenance = json.loads((package / "provenance.json").read_text(encoding="utf-8"))
    manifest = yaml.safe_load((ROOT / "sources" / "manifest.yaml").read_text(encoding="utf-8"))
    registered = {source["id"] for source in manifest["sources"]}
    claims = provenance.get("curriculum_claims", [])
    if {claim.get("competency") for claim in claims} != set(assessment.get("competencies", [])):
        errors.append("assessment provenance does not cover every competency")
    if any(claim.get("source_id") not in registered or not claim.get("printed_pages") for claim in claims):
        errors.append("assessment provenance contains an unregistered or unlocated claim")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packages", nargs="*", type=Path)
    args = parser.parse_args(argv)
    packages = args.packages or sorted((ROOT / "content" / "lessons").glob("unit-*/competency-*"))
    errors: list[str] = []
    for package in packages:
        errors.extend(f"{package}: {error}" for error in validate_lesson_package(package))
    assessments = sorted((ROOT / "assessments" / "unit-tests").glob("unit-*")) if not args.packages else []
    for package in assessments:
        errors.extend(f"{package}: {error}" for error in validate_assessment_package(package))
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors))
        return 1
    print(f"Validated {len(packages)} lesson package(s) and {len(assessments)} assessment package(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
