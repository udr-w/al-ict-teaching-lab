---
name: ingest-official-sources
description: Ingest, register, extract, and normalize official syllabus and teacher-guide material. Use when adding authoritative curriculum sources or refreshing source-derived curriculum data.
---

# Ingest official sources

1. Place the original artifact under sources/official without altering it.
2. Add stable metadata, checksum, publication details, and authority to sources/manifest.yaml.
3. Extract structured content with scripts/ when available.
4. Preserve page or section references for every extracted claim.
5. Record unresolved source disagreement in sources/conflicts/curriculum-conflicts.yaml.
6. Validate provenance before updating curriculum artifacts.
