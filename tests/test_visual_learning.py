import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGES = [
    ROOT / "content" / "lessons" / "unit-01" / "competency-1.1",
    ROOT / "content" / "lessons" / "unit-01" / "competency-1.2",
]


def test_quarto_deck_maps_notes_and_stable_ids_to_every_slide() -> None:
    for package in PACKAGES:
        source = (package / "slides.qmd").read_text(encoding="utf-8")
        slides = re.findall(r"^## .+?\{#([a-z0-9-]+)\}\s*$", source, re.MULTILINE)
        notes = re.findall(r"^::: \{\.notes\}\s*$", source, re.MULTILINE)
        assert len(slides) >= 10
        assert len(notes) == len(slides)
        assert len(set(slides)) == len(slides)


def test_deck_uses_meaningful_offline_visuals_with_descriptions() -> None:
    for package in PACKAGES:
        source = (package / "slides.qmd").read_text(encoding="utf-8")
        images = re.findall(r'!\[\]\((assets/[^)]+\.svg)\)\{[^}]*fig-alt="([^"]+)"[^}]*\}', source)
        assert len(images) >= 6
        assert all(alt.strip() for _, alt in images)
        assert source.count("Long description:") >= len(images)
        for relative_path, _ in images:
            assert (package / relative_path).is_file()


def test_deck_corrects_calculation_comparison_conclusion_distinction() -> None:
    package = PACKAGES[0]
    source = (package / "slides.qmd").read_text(encoding="utf-8")
    assert "**1 · Calculate**" in source
    assert "**2 · Compare**" in source
    assert "**3 · Conclude—with context**" in source
    assert "before changing staffing" in source


def test_competency_1_2_separates_network_and_mobile_concepts() -> None:
    source = (PACKAGES[1] / "slides.qmd").read_text(encoding="utf-8")
    lowered = source.lower()
    for phrase in ["internet ≠ world wide web", "mobile communication", "mobile computing", "cloud service"]:
        assert phrase in lowered
    assert "Cloud is not a synonym for the Internet" in source
