from pathlib import Path

import yaml

from scripts.validate_package import validate_assessment_package


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "assessments" / "unit-tests" / "unit-01"


def test_unit_1_assessment_package_is_valid() -> None:
    assert validate_assessment_package(PACKAGE) == []


def test_blueprint_balances_marks_and_cognitive_demand() -> None:
    blueprint = yaml.safe_load((PACKAGE / "blueprint.yaml").read_text(encoding="utf-8"))["blueprint"]
    assert sum(blueprint["competency_mark_totals"].values()) == 40
    assert sum(blueprint["cognitive_mark_totals"].values()) == 40
    assert set(blueprint["cognitive_mark_totals"]) == {"understand", "apply", "analyse", "evaluate"}
