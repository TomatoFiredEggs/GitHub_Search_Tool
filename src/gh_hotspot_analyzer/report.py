from __future__ import annotations

from html import escape
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


def render_html_report(analysis: dict) -> str:
    summary = analysis["summary"]
    language_bars = render_metric_bars(analysis["language_distribution"])
    topic_bars = render_metric_bars(analysis["topic_distribution"])
    top_rows = "\n".join(
        [
            "<tr>"
            f"<td>{index}</td>"
            f"<td><a href=\"{escape(repo['html_url'])}\">{escape(repo['full_name'])}</a></td>"
            f"<td>{escape(repo['language'])}</td>"
            f"<td>{repo['stars']}</td>"
            f"<td>{repo['score']}</td>"
            f"<td>{escape(repo['updated_at'][:10])}</td>"
            "</tr>"
            for index, repo in enumerate(analysis["top_repositories"], start=1)
        ]
    )
    active_cards = "\n".join(
        [
            "<article class=\"mini-card\">"
            f"<h3><a href=\"{escape(repo['html_url'])}\">{escape(repo['full_name'])}</a></h3>"
            f"<p>Inactive for {repo['inactive_days']} day(s)</p>"
            f"<strong>Score {repo['score']}</strong>"
            "</article>"
            for repo in analysis["most_active"]
        ]
    )
    opportunity_cards = "\n".join(
        [
            "<article class=\"mini-card\">"
            f"<h3><a href=\"{escape(repo['html_url'])}\">{escape(repo['full_name'])}</a></h3>"
            f"<p>Created {repo['freshness_days']} day(s) ago</p>"
            f"<strong>{repo['stars']} stars</strong>"
            "</article>"
            for repo in analysis["new_opportunities"]
        ]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GitHub Hotspot Dashboard</title>
  <style>
    :root {{
      --bg: #f4f1e8;
      --panel: #fffdf8;
      --ink: #1f2a1f;
      --muted: #5f6b61;
      --line: #d8d0c2;
      --accent: #0f766e;
      --accent-soft: #d7efe7;
      --accent-warm: #d97706;
      --shadow: 0 16px 40px rgba(31, 42, 31, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background:
        radial-gradient(circle at top left, rgba(15, 118, 110, 0.14), transparent 32%),
        radial-gradient(circle at top right, rgba(217, 119, 6, 0.14), transparent 28%),
        var(--bg);
      color: var(--ink);
    }}
    .page {{
      max-width: 1160px;
      margin: 0 auto;
      padding: 48px 20px 64px;
    }}
    .hero {{
      padding: 28px;
      border: 1px solid var(--line);
      background: linear-gradient(135deg, rgba(255,253,248,0.98), rgba(215,239,231,0.82));
      border-radius: 28px;
      box-shadow: var(--shadow);
    }}
    .eyebrow {{
      margin: 0 0 12px;
      font-size: 12px;
      letter-spacing: 0.2em;
      text-transform: uppercase;
      color: var(--accent);
    }}
    h1, h2, h3, p {{
      margin-top: 0;
    }}
    h1 {{
      margin-bottom: 12px;
      font-size: clamp(36px, 6vw, 64px);
      line-height: 0.95;
    }}
    .hero p {{
      max-width: 780px;
      color: var(--muted);
      font-size: 18px;
    }}
    .stats {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-top: 24px;
    }}
    .stat-card, .panel, .mini-card {{
      border: 1px solid var(--line);
      background: var(--panel);
      border-radius: 22px;
      box-shadow: var(--shadow);
    }}
    .stat-card {{
      padding: 18px 20px;
    }}
    .stat-card span {{
      display: block;
      margin-bottom: 8px;
      color: var(--muted);
      font-size: 14px;
    }}
    .stat-card strong {{
      font-size: 28px;
    }}
    .layout {{
      display: grid;
      grid-template-columns: 1.8fr 1fr;
      gap: 20px;
      margin-top: 24px;
    }}
    .panel {{
      padding: 22px;
    }}
    .panel-header {{
      display: flex;
      align-items: baseline;
      justify-content: space-between;
      gap: 12px;
    }}
    .panel-header p {{
      color: var(--muted);
      margin-bottom: 0;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 16px;
      font-size: 14px;
    }}
    th, td {{
      padding: 12px 10px;
      border-bottom: 1px solid var(--line);
      text-align: left;
      vertical-align: top;
    }}
    th {{
      color: var(--muted);
      font-weight: 600;
    }}
    a {{
      color: var(--accent);
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    .bars {{
      display: grid;
      gap: 12px;
      margin-top: 14px;
    }}
    .bar-row {{
      display: grid;
      grid-template-columns: 120px 1fr auto;
      align-items: center;
      gap: 12px;
      font-size: 14px;
    }}
    .bar-track {{
      height: 12px;
      border-radius: 999px;
      background: #efe8da;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      border-radius: 999px;
      background: linear-gradient(90deg, var(--accent), var(--accent-warm));
    }}
    .stack {{
      display: grid;
      gap: 20px;
    }}
    .mini-grid {{
      display: grid;
      gap: 14px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    .mini-card {{
      padding: 18px;
    }}
    .mini-card p {{
      color: var(--muted);
      margin-bottom: 10px;
    }}
    @media (max-width: 900px) {{
      .layout {{
        grid-template-columns: 1fr;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <p class="eyebrow">Open Source Momentum Tracker</p>
      <h1>GitHub Hotspot Dashboard</h1>
      <p>Snapshot generated at {escape(analysis['generated_at'])}. This report summarizes the hottest repositories in the current dataset and highlights language concentration, active projects, and newly emerging opportunities.</p>
      <div class="stats">
        <article class="stat-card"><span>Total Repositories</span><strong>{summary['total_repositories']}</strong></article>
        <article class="stat-card"><span>Top Language</span><strong>{escape(summary['top_language'])}</strong></article>
        <article class="stat-card"><span>Average Score</span><strong>{summary['average_score']}</strong></article>
      </div>
    </section>
    <section class="layout">
      <div class="stack">
        <section class="panel">
          <div class="panel-header">
            <h2>Top Repositories</h2>
            <p>Ranked by hotspot score</p>
          </div>
          <table>
            <thead>
              <tr><th>#</th><th>Repository</th><th>Language</th><th>Stars</th><th>Score</th><th>Updated</th></tr>
            </thead>
            <tbody>
              {top_rows}
            </tbody>
          </table>
        </section>
        <section class="panel">
          <div class="panel-header">
            <h2>Opportunity Watchlist</h2>
            <p>Recent repositories worth following</p>
          </div>
          <div class="mini-grid">
            {opportunity_cards}
          </div>
        </section>
      </div>
      <div class="stack">
        <section class="panel">
          <div class="panel-header">
            <h2>Language Mix</h2>
            <p>Distribution in this snapshot</p>
          </div>
          <div class="bars">{language_bars}</div>
        </section>
        <section class="panel">
          <div class="panel-header">
            <h2>Topic Signals</h2>
            <p>Most common repository tags</p>
          </div>
          <div class="bars">{topic_bars}</div>
        </section>
        <section class="panel">
          <div class="panel-header">
            <h2>Most Active</h2>
            <p>Projects updated most recently</p>
          </div>
          <div class="mini-grid">
            {active_cards}
          </div>
        </section>
      </div>
    </section>
  </main>
</body>
</html>
"""


def save_report(report_content: str, output_path: str | Path | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else REPORTS_DIR / default_report_filename()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_content, encoding="utf-8")
    return target


def default_report_filename() -> str:
    return f"github_hotspot_report_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.md"


def save_html_report(report_content: str, output_path: str | Path | None = None) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else REPORTS_DIR / default_html_report_filename()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(report_content, encoding="utf-8")
    return target


def default_html_report_filename() -> str:
    return f"github_hotspot_dashboard_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.html"


def render_metric_bars(distribution: dict[str, int]) -> str:
    if not distribution:
        return '<p class="empty">No data available.</p>'

    peak = max(distribution.values())
    rows = []
    for label, value in distribution.items():
        width = round((value / peak) * 100, 2) if peak else 0
        rows.append(
            "<div class=\"bar-row\">"
            f"<span>{escape(label)}</span>"
            f"<div class=\"bar-track\"><div class=\"bar-fill\" style=\"width: {width}%\"></div></div>"
            f"<strong>{value}</strong>"
            "</div>"
        )
    return "\n".join(rows)
