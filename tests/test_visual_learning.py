import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "content" / "lessons" / "unit-01" / "competency-1.1"


def test_quarto_deck_maps_notes_and_stable_ids_to_every_slide() -> None:
    source = (PACKAGE / "slides.qmd").read_text(encoding="utf-8")
    slides = re.findall(r"^## .+?\{#([a-z0-9-]+)\}\s*$", source, re.MULTILINE)
    notes = re.findall(r"^::: \{\.notes\}\s*$", source, re.MULTILINE)
    assert len(slides) == 10
    assert len(notes) == len(slides)
    assert len(set(slides)) == len(slides)


def test_deck_uses_meaningful_offline_visuals_with_descriptions() -> None:
    source = (PACKAGE / "slides.qmd").read_text(encoding="utf-8")
    images = re.findall(r'!\[\]\((assets/[^)]+\.svg)\)\{[^}]*fig-alt="([^"]+)"[^}]*\}', source)
    assert len(images) >= 6
    assert all(alt.strip() for _, alt in images)
    assert source.count("Long description:") >= len(images)
    for relative_path, _ in images:
        assert (PACKAGE / relative_path).is_file()


def test_deck_corrects_calculation_comparison_conclusion_distinction() -> None:
    source = (PACKAGE / "slides.qmd").read_text(encoding="utf-8")
    assert "**1 · Calculate**" in source
    assert "**2 · Compare**" in source
    assert "**3 · Conclude—with context**" in source
    assert "before changing staffing" in source
