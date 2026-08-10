from pathlib import Path

import yaml

from scripts.validate_publication import validate_publication


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "content" / "lessons" / "unit-01" / "competency-1.1"


def test_publication_source_has_no_privacy_or_draft_blockers() -> None:
    # Rendered candidates are generated outside the test; source-level blockers
    # would still be present after excluding missing generated artifacts.
    blockers, _ = validate_publication(PACKAGE)
    source_blockers = [item for item in blockers if not item.startswith("rendered artifact")]
    assert source_blockers == []


def test_slide_formats_have_an_explicit_accessibility_contract() -> None:
    publication = yaml.safe_load((PACKAGE / "publication.yaml").read_text(encoding="utf-8"))["publication"]
    assert publication["format_accessibility"] == {
        "slides_html": "primary-accessible-format",
        "slides_pdf": "print-reference-untagged",
    }
    assert publication["status"] == "publication-candidate"
    assert publication["release_checks"]["accessibility"] == "blocked-untagged-slide-pdf"
