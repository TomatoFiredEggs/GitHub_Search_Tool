# GitHub Hotspot Analyzer

GitHub Hotspot Analyzer is a lightweight data analysis project for tracking recently popular open source repositories on GitHub. It fetches repository snapshots, scores them with a simple ranking model, and produces readable Markdown reports for review, sharing, or personal research.

## Why This Project Exists

When browsing GitHub manually, it is easy to notice isolated trending repositories but hard to compare them consistently over time. This project was built to solve three practical problems:

- capture a reproducible snapshot instead of relying on the live UI
- rank repositories with a transparent scoring model
- compare multiple snapshots to see which projects are gaining momentum

## Features

- Fetch hot repositories from the GitHub Search API
- Save raw JSON snapshots for reproducible analysis
- Score repositories using stars, forks, watchers, freshness, and activity
- Generate Markdown reports for a single snapshot
- Generate static HTML dashboards for a single snapshot
- Compare two snapshots to detect new entries, star growth, rank changes, and language shifts
- Run fully offline with bundled example datasets

## Project Layout

```text
.
|-- data/
|   |-- examples/
|   `-- raw/
|-- reports/
|-- src/
|   `-- gh_hotspot_analyzer/
`-- tests/
```

## Quick Start

### Install

```bash
pip install -e .
```

### Configure GitHub Token

Copy `.env.example` to `.env` and fill in a GitHub token:

```env
GITHUB_TOKEN=ghp_xxx
```

The token is optional, but strongly recommended because unauthenticated API requests are rate-limited.

### Fetch a Snapshot and Build a Report

```bash
gh-hotspot run --days 30 --limit 30
```

Outputs:

- raw snapshots are written to `data/raw/`
- reports are written to `reports/`

## Commands

Fetch data:

```bash
gh-hotspot fetch --days 14 --limit 20 --output data/raw/snapshot.json
```

Analyze a local snapshot as JSON:

```bash
gh-hotspot analyze --input data/raw/snapshot.json
```

Generate a Markdown report:

```bash
gh-hotspot report --input data/raw/snapshot.json --output reports/hotspot-report.md
```

Generate a static HTML dashboard:

```bash
gh-hotspot html-report --input data/raw/snapshot.json --output reports/hotspot-dashboard.html
```

Compare two snapshots:

```bash
gh-hotspot compare --previous data/examples/sample_payload_previous.json --current data/examples/sample_payload.json --output reports/comparison-report.md
```

Run tests:

```bash
python -m unittest discover -s tests
```

## Offline Demo

This repository includes bundled example data so the full workflow can be demonstrated without network access.

Single snapshot report:

```bash
gh-hotspot report --input data/examples/sample_payload.json --output reports/sample-report.md
```

Single snapshot HTML dashboard:

```bash
gh-hotspot html-report --input data/examples/sample_payload.json --output reports/sample-dashboard.html
```

Snapshot comparison report:

```bash
gh-hotspot compare --previous data/examples/sample_payload_previous.json --current data/examples/sample_payload.json --output reports/sample-comparison-report.md
```

## Analysis Model

The current hotspot score combines:

- stargazers
- forks
- watchers
- recent creation bonus
- recent update bonus
- open issue penalty

The goal is not to produce a perfect ranking model. The goal is to provide a simple, inspectable baseline that can be iterated on later.

## What The Comparison Report Highlights

- newly appeared repositories in the latest snapshot
- repositories with the largest star increase
- repositories that climbed in ranking
- changes in language distribution between snapshots

## Roadmap

- add historical snapshots over more than two periods
- generate HTML charts and dashboards
- support scheduled daily report generation
- classify projects by topic clusters

## License

MIT
