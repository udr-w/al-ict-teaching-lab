from pathlib import Path

import yaml

from scripts.ingest_sources import REPOSITORY_ROOT, verify_sources


MANIFEST = REPOSITORY_ROOT / "sources" / "manifest.yaml"


def test_registered_sources_are_present_and_unchanged() -> None:
    assert verify_sources(MANIFEST) == []


def test_course_curriculum_source_is_registered() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    course_path = REPOSITORY_ROOT / "config" / "course.yaml"
    course = yaml.safe_load(course_path.read_text(encoding="utf-8"))["course"]
    source_ids = {source["id"] for source in manifest["sources"]}
    assert course["curriculum_source"] in source_ids
    assert set(course.get("supporting_sources", [])) <= source_ids


def test_official_artifacts_stay_under_sources_official() -> None:
    manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    for source in manifest["sources"]:
        path = Path(source["local_path"])
        assert path.parts[:2] == ("sources", "official")
