"""Verify registered source artifacts before curriculum extraction."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import yaml


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def verify_sources(manifest_path: Path) -> list[str]:
    """Return validation errors for artifacts registered in a source manifest."""
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8")) or {}
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        return ["manifest must register at least one source"]

    errors: list[str] = []
    seen_ids: set[str] = set()
    required = {"id", "type", "authority", "source_url", "local_path", "sha256"}

    for index, source in enumerate(sources, start=1):
        if not isinstance(source, dict):
            errors.append(f"source {index} must be a mapping")
            continue

        missing = sorted(required - source.keys())
        label = source.get("id", f"source {index}")
        if missing:
            errors.append(f"{label}: missing {', '.join(missing)}")
            continue
        if source["id"] in seen_ids:
            errors.append(f"{label}: duplicate source id")
        seen_ids.add(source["id"])

        artifact = REPOSITORY_ROOT / source["local_path"]
        if not artifact.is_file():
            errors.append(f"{label}: artifact not found: {source['local_path']}")
            continue
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        if digest != source["sha256"]:
            errors.append(f"{label}: checksum mismatch")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=REPOSITORY_ROOT / "sources" / "manifest.yaml",
    )
    args = parser.parse_args(argv)
    errors = verify_sources(args.manifest)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Verified all registered source artifacts.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
