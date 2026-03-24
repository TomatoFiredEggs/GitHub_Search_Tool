# GitHub Hotspot Analyzer

A small but real portfolio project that fetches hot open source repositories from GitHub, scores them, and generates a readable Markdown report.

## What It Does

- Fetches recently created popular repositories through the GitHub Search API
- Stores raw snapshots locally for reproducible analysis
- Computes a hotspot score from stars, forks, watchers, freshness, and activity
- Generates a Markdown report you can publish or review locally

## Project Layout

```text
.
├─ data/
│  ├─ examples/
│  └─ raw/
├─ reports/
├─ src/
│  └─ gh_hotspot_analyzer/
└─ tests/
```

## Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Configure

Copy `.env.example` to `.env` and set your GitHub token:

```env
GITHUB_TOKEN=ghp_xxx
```

You can still run the project without a token, but GitHub API rate limits will be much lower.

### 3. Fetch and generate a report

```bash
gh-hotspot run --days 30 --limit 30
```

Generated files:

- raw payloads go to `data/raw/`
- Markdown reports go to `reports/`

## Example Commands

```bash
gh-hotspot fetch --days 14 --limit 20 --output data/raw/sample.json
gh-hotspot analyze --input data/raw/sample.json
gh-hotspot report --input data/raw/sample.json --output reports/manual-report.md
python -m unittest discover -s tests
```

## Offline Demo

The repository includes a sample payload so the project can be demonstrated without hitting the network:

```bash
gh-hotspot analyze --input data/examples/sample_payload.json
gh-hotspot report --input data/examples/sample_payload.json --output reports/sample-report.md
```

## Suggested Commit Sequence

If you want this repository to reflect real work, keep the history honest and incremental:

1. `chore: initialize project skeleton`
2. `feat: add github repository fetcher`
3. `feat: implement repository scoring and analytics`
4. `feat: generate markdown hotspot report`
5. `test: add analyzer unit tests`
6. `docs: improve setup and usage notes`

## Next Iterations

- Add historical snapshot comparison
- Generate charts in HTML
- Add scheduled daily reports
- Classify projects by topic clusters

## License

MIT
