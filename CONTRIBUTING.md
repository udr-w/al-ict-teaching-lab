# Contributing

Thanks for helping improve `al-ict-teaching-lab`.

## Before contributing

Read `README.md`, `AGENTS.md`, and the relevant files under `docs/`. Keep changes aligned with the project goal: teaching Sri Lankan GCE A/L ICT in a curriculum-aware, practical, student-friendly way.

## Development setup

1. Install the pinned presentation tooling described in `README.md`.
2. Install Python development dependencies with:

   ```bash
   uv sync --extra dev
   ```

3. Run the test suite before submitting changes:

   ```bash
   uv run --extra dev python -m pytest
   ```

4. Run package validation when changing teaching or publication material:

   ```bash
   uv run --extra dev python scripts/validate_package.py
   ```

## Contribution rules

- Keep official syllabus and teacher-guide provenance intact.
- Do not invent curriculum claims when the official sources are unclear.
- Do not commit raw official PDFs, past-paper PDFs, learner-identifiable information, credentials, tokens, caches, or generated local outputs that are intentionally ignored.
- Use synthetic or anonymized learner data only.
- Keep student-facing material free from teacher answers, internal lifecycle text, and hidden future prerequisites.
- Record source and licence information for external visual assets.
- Prefer focused changes with tests over broad rewrites.
- Do not mark generated teaching material as published or classroom-validated without the required human approval and evidence.

## Teaching-material changes

When changing lessons, assessments, slides, student packs, or practicals, verify:

- curriculum and concept alignment;
- prerequisite safety;
- student/teacher audience separation;
- answer correctness;
- render quality and overflow;
- accessibility and paper/offline fallback where applicable;
- relevant review evidence.

## Pull requests

Explain what changed, why it matters, and how it was verified. Include screenshots or rendered-review evidence when a change materially affects student-facing visuals.

Security or privacy issues should not be filed publicly. Follow `.github/SECURITY.md`.
