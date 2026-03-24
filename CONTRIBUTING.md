# Contributing Guide

## Development Workflow

Use small, reviewable commits instead of one large dump.

Suggested flow:

1. Create the project skeleton and documentation
2. Implement the GitHub fetcher
3. Add scoring and analytics logic
4. Add report generation
5. Add tests and sample data
6. Refine docs after running the project end to end

## Commit Convention

Recommended prefixes:

- `feat`: new user-facing functionality
- `fix`: bug fix
- `refactor`: internal cleanup without behavior change
- `test`: add or improve tests
- `docs`: documentation only
- `chore`: repository maintenance

Examples:

- `chore: initialize repository structure`
- `feat: add github search api fetcher`
- `feat: implement hotspot ranking model`
- `feat: generate markdown report from repository snapshot`
- `test: cover analyzer summary and ranking behavior`
- `docs: document setup and offline demo usage`

## Local Validation

```bash
python -m unittest discover -s tests
python -m gh_hotspot_analyzer.cli report --input data/examples/sample_payload.json --output reports/sample-report.md
```

## Notes

- Keep raw API snapshots out of version control unless they are intentionally curated examples
- Prefer updating the sample payload when changing report behavior
- If you add a new metric, document the scoring rationale in `README.md`

