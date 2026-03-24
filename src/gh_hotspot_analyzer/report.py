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


def render_comparison_report(comparison: dict) -> str:
    lines = [
        "# GitHub Hotspot Comparison Report",
        "",
        f"- Generated at: {comparison['generated_at']}",
        f"- Previous repositories: {comparison['previous_summary']['total_repositories']}",
        f"- Current repositories: {comparison['current_summary']['total_repositories']}",
        f"- Previous top language: {comparison['previous_summary']['top_language']}",
        f"- Current top language: {comparison['current_summary']['top_language']}",
        "",
        "## New Entries",
        "",
    ]

    if comparison["new_entries"]:
        for repo in comparison["new_entries"]:
            lines.append(
                f"- [{repo['full_name']}]({repo['html_url']}): {repo['current_stars']} stars, language {repo['language']}"
            )
    else:
        lines.append("- No new repositories entered the snapshot.")

    lines.extend(["", "## Top Star Gainers", ""])
    if comparison["top_star_gainers"]:
        for repo in comparison["top_star_gainers"]:
            lines.append(
                f"- [{repo['full_name']}]({repo['html_url']}): +{repo['stars_delta']} stars "
                f"({repo['previous_stars']} -> {repo['current_stars']})"
            )
    else:
        lines.append("- No overlapping repositories were found.")

    lines.extend(["", "## Top Rank Climbers", ""])
    if comparison["top_rank_climbers"]:
        for repo in comparison["top_rank_climbers"]:
            lines.append(
                f"- [{repo['full_name']}]({repo['html_url']}): up {repo['rank_delta']} positions "
                f"({repo['previous_rank']} -> {repo['current_rank']})"
            )
    else:
        lines.append("- No repositories improved their rank between the two snapshots.")

    lines.extend(["", "## Language Changes", ""])
    if comparison["language_changes"]:
        for item in comparison["language_changes"]:
            sign = "+" if item["delta"] > 0 else ""
            lines.append(
                f"- {item['language']}: {item['previous_count']} -> {item['current_count']} ({sign}{item['delta']})"
            )
    else:
        lines.append("- No language distribution changes detected.")

    return "\n".join(lines) + "\n"


def save_report(report_content: str, output_path: str | Path | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else REPORTS_DIR / default_report_filename()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_content, encoding="utf-8")
    return target


def default_report_filename() -> str:
    return f"github_hotspot_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"
