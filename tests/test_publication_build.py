from pathlib import Path

from scripts.build_publications import candidate_packages


ROOT = Path(__file__).resolve().parents[1]


def test_every_publication_manifest_is_discovered_for_rebuild() -> None:
    packages = candidate_packages()
    assert [package.name for package in packages] == ["competency-1.1", "competency-1.2"]
    assert all(package.is_relative_to(ROOT / "content" / "lessons") for package in packages)
