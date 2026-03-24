from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .config import REPORTS_DIR


def render_report(analysis: dict) -> str:
    summary = analysis["summary"]
    lines = [
        "# GitHub Hotspot Report",
        "",
        f"- Generated at: {analysis['generated_at']}",
        f"- Total repositories: {summary['total_repositories']}",
        f"- Top language: {summary['top_language']}",
        f"- Average score: {summary['average_score']}",
        "",
        "## Top Repositories",
        "",
        "| Rank | Repository | Language | Stars | Score | Updated |",
        "| --- | --- | --- | ---: | ---: | --- |",
    ]

    for index, repo in enumerate(analysis["top_repositories"], start=1):
        lines.append(
            f"| {index} | [{repo['full_name']}]({repo['html_url']}) | {repo['language']} | "
            f"{repo['stars']} | {repo['score']} | {repo['updated_at'][:10]} |"
        )

    lines.extend(
        [
            "",
            "## Language Distribution",
            "",
        ]
    )
    for language, count in analysis["language_distribution"].items():
        lines.append(f"- {language}: {count}")

    lines.extend(
        [
            "",
            "## Topic Distribution",
            "",
        ]
    )
    for topic, count in analysis["topic_distribution"].items():
        lines.append(f"- {topic}: {count}")

    lines.extend(
        [
            "",
            "## Most Active Repositories",
            "",
        ]
    )
    for repo in analysis["most_active"]:
        lines.append(
            f"- [{repo['full_name']}]({repo['html_url']}): inactive {repo['inactive_days']} days, score {repo['score']}"
        )

    lines.extend(
        [
            "",
            "## New Opportunities",
            "",
        ]
    )
    for repo in analysis["new_opportunities"]:
        lines.append(
            f"- [{repo['full_name']}]({repo['html_url']}): created {repo['freshness_days']} days ago, "
            f"stars {repo['stars']}, score {repo['score']}"
        )

    return "\n".join(lines) + "\n"


def save_report(report_content: str, output_path: str | Path | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else REPORTS_DIR / default_report_filename()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_content, encoding="utf-8")
    return target


def default_report_filename() -> str:
    return f"github_hotspot_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"

