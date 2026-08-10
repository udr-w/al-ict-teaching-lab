# AL ICT Teaching Lab

A structured workspace for planning, producing, assessing, and improving Sri Lankan GCE Advanced Level ICT teaching materials.

## Layout

Official inputs live in sources/, curriculum models in curriculum/, teaching packages in content/, assessment materials in assessments/, and generated releases in published/. Cohort-specific and private learner evidence stays under cohorts/.

## Getting started

1. Configure the course and policies in config/.
2. Register source documents in sources/manifest.yaml.
3. Build the curriculum model and teaching packages.
4. Install the pinned presentation tools with `scripts/bootstrap_quarto.sh`, `scripts/bootstrap_node.sh`, and `PUPPETEER_SKIP_DOWNLOAD=true npm ci --ignore-scripts`.
5. Install Python development dependencies with `uv sync --extra dev`.
6. Run `uv run --extra dev python scripts/validate_package.py` before publication.

## Publication artifacts

`content/` is the canonical source. `outputs/` contains reproducible publication candidates and remains untracked. `published/` is also generated and is reserved for packages that have passed every release gate; do not copy a candidate there merely because it renders successfully.

Rebuild every current publication candidate from a clean checkout with:

```bash
uv run --extra dev python scripts/build_publications.py
```

The command renders the slide HTML/PDF and all teacher/learner documents, then runs each package's publication validator. Competencies 1.1 and 1.2 currently remain candidates because their slide PDFs are untagged; their self-contained HTML decks are the primary accessible formats.
