from pathlib import Path

from scripts.validate_package import validate_lesson_package


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "content" / "lessons" / "unit-01" / "competency-1.1"


def test_competency_1_1_package_is_complete() -> None:
    assert validate_lesson_package(PACKAGE) == []


def test_answers_cover_worksheet_and_homework() -> None:
    answers = (PACKAGE / "answers.md").read_text(encoding="utf-8")
    assert "## Worksheet" in answers
    assert "## Homework" in answers
    for number in range(1, 15):
        assert f"{number}." in answers
