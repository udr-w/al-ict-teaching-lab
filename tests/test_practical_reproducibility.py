from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRACTICAL = ROOT / "content" / "lessons" / "unit-01" / "competency-1.1" / "practical.md"


def test_practical_contains_reproducibility_and_privacy_guidance() -> None:
    text = PRACTICAL.read_text(encoding="utf-8")
    for heading in ["## Dataset", "## Task", "## Expected results", "## Validation checklist", "## Troubleshooting", "## Safety and privacy"]:
        assert heading in text
    assert "fictional" in text.lower()
    assert "Total: 110" in text
