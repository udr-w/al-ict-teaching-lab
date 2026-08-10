from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRACTICALS = {
    "1.1": ROOT / "content" / "lessons" / "unit-01" / "competency-1.1" / "practical.md",
    "1.2": ROOT / "content" / "lessons" / "unit-01" / "competency-1.2" / "practical.md",
}


def test_practical_contains_reproducibility_and_privacy_guidance() -> None:
    for text in (path.read_text(encoding="utf-8") for path in PRACTICALS.values()):
        for heading in ["## Dataset", "## Task", "## Expected results", "## Validation checklist", "## Troubleshooting", "## Safety and privacy"]:
            assert heading in text
        assert "fictional" in text.lower()
    assert "Total: 110" in PRACTICALS["1.1"].read_text(encoding="utf-8")
    scaled = PRACTICALS["1.2"].read_text(encoding="utf-8")
    assert "P = 14, N = 16, L = 10" in scaled
    assert "include data entry in the timed workflow" in scaled
