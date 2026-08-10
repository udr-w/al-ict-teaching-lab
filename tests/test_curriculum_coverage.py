import csv
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
UNITS = ROOT / "curriculum" / "units"
MANIFEST = ROOT / "sources" / "manifest.yaml"


def load_units() -> list[dict]:
    return [
        yaml.safe_load(path.read_text(encoding="utf-8"))["unit"]
        for path in sorted(UNITS.glob("*.yaml"))
    ]


def test_curriculum_levels_have_source_and_periods() -> None:
    source_ids = {
        source["id"]
        for source in yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))["sources"]
    }
    for unit in load_units():
        assert unit["source"]["id"] in source_ids
        assert unit["source"]["printed_pages"]
        assert unit["competency_levels"]
        for level in unit["competency_levels"]:
            assert level["id"].startswith(f"{unit['id']}.")
            assert level["outcome"]
            assert level["periods"] > 0
            assert level["source_printed_pages"]


def test_coverage_matrix_matches_modelled_levels() -> None:
    expected = {
        level["id"] for unit in load_units() for level in unit["competency_levels"]
    }
    matrix_path = ROOT / "curriculum" / "coverage-matrix.csv"
    with matrix_path.open(encoding="utf-8", newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert {row["learning_outcome_id"] for row in rows} == expected
    assert all(row["status"] == "modelled" for row in rows)


def test_units_match_syllabus_period_totals() -> None:
    totals = {
        unit["id"]: sum(level["periods"] for level in unit["competency_levels"])
        for unit in load_units()
    }
    assert totals == {
        1: 34,
        2: 15,
        3: 19,
        4: 14,
        5: 14,
        6: 19,
        7: 85,
        8: 71,
        9: 53,
        10: 44,
        11: 38,
        12: 15,
        13: 20,
        14: 30,
    }
    assert sum(totals.values()) == 471


def test_term_schedule_covers_each_level_once_with_correct_load() -> None:
    units = load_units()
    periods_by_level = {
        level["id"]: level["periods"]
        for unit in units
        for level in unit["competency_levels"]
    }
    schedule_path = ROOT / "cohorts" / "2027-a" / "schedule.yaml"
    schedule = yaml.safe_load(schedule_path.read_text(encoding="utf-8"))["schedule"]
    scheduled = [
        level
        for term in schedule["terms"]
        for level in term["competency_levels"]
    ]
    assert len(scheduled) == len(set(scheduled))
    assert set(scheduled) == set(periods_by_level)
    for term in schedule["terms"]:
        assert term["periods"] == sum(
            periods_by_level[level] for level in term["competency_levels"]
        )


def test_dependency_graph_covers_units_and_is_acyclic() -> None:
    graph_path = ROOT / "curriculum" / "dependency-graph.yaml"
    graph = yaml.safe_load(graph_path.read_text(encoding="utf-8"))
    node_ids = {node["id"] for node in graph["nodes"]}
    assert node_ids == {unit["id"] for unit in load_units()}

    outgoing = {node_id: [] for node_id in node_ids}
    indegree = {node_id: 0 for node_id in node_ids}
    for edge in graph["edges"]:
        assert edge["from"] in node_ids and edge["to"] in node_ids
        assert edge["from"] != edge["to"]
        assert edge["rationale"]
        outgoing[edge["from"]].append(edge["to"])
        indegree[edge["to"]] += 1

    ready = [node_id for node_id, degree in indegree.items() if degree == 0]
    visited = 0
    while ready:
        node_id = ready.pop()
        visited += 1
        for successor in outgoing[node_id]:
            indegree[successor] -= 1
            if indegree[successor] == 0:
                ready.append(successor)
    assert visited == len(node_ids)


def test_dependency_exposure_order_agrees_with_official_schedule() -> None:
    schedule_path = ROOT / "cohorts" / "2027-a" / "schedule.yaml"
    terms = yaml.safe_load(schedule_path.read_text(encoding="utf-8"))["schedule"]["terms"]
    sequence = [level for term in terms for level in term["competency_levels"]]
    first_exposure: dict[int, int] = {}
    for position, level in enumerate(sequence):
        first_exposure.setdefault(int(level.split(".")[0]), position)

    graph_path = ROOT / "curriculum" / "dependency-graph.yaml"
    edges = yaml.safe_load(graph_path.read_text(encoding="utf-8"))["edges"]
    for edge in edges:
        assert first_exposure[edge["from"]] < first_exposure[edge["to"]]


def test_cohort_coverage_tracks_every_existing_lesson_package() -> None:
    coverage_path = ROOT / "cohorts" / "2027-a" / "coverage.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8"))["units"]
    tracked = {
        competency_id: details
        for unit in coverage.values()
        for competency_id, details in unit["competencies"].items()
    }
    package_ids = {
        path.name.removeprefix("competency-")
        for path in (ROOT / "content" / "lessons").glob("unit-*/competency-*")
        if path.is_dir()
    }
    assert package_ids <= set(tracked)
    for competency_id in package_ids:
        assert tracked[competency_id]["lesson_package"] in {
            "ready-for-review",
            "publication-candidate",
            "publication-ready",
        }

    assessment_ids = {
        yaml.safe_load(path.read_text(encoding="utf-8"))["assessment"]["id"]
        for path in (ROOT / "assessments").glob("**/assessment.yaml")
    }
    for details in tracked.values():
        if "assessment" in details:
            assert details["assessment"] in assessment_ids
