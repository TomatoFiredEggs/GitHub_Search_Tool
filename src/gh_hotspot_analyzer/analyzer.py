from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


@dataclass(slots=True)
class RepoInsight:
    full_name: str
    html_url: str
    description: str
    language: str
    stars: int
    forks: int
    watchers: int
    open_issues: int
    created_at: str
    updated_at: str
    topics: list[str]
    score: float
    freshness_days: int
    inactive_days: int


def compute_score(repo: dict[str, Any], now: datetime | None = None) -> float:
    now = now or datetime.now(UTC)
    created_at = parse_iso_datetime(repo["created_at"])
    updated_at = parse_iso_datetime(repo["updated_at"])
    freshness_days = max((now - created_at).days, 0)
    inactive_days = max((now - updated_at).days, 0)

    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    watchers = repo.get("watchers_count", 0)
    open_issues = repo.get("open_issues_count", 0)

    freshness_bonus = max(0, 30 - freshness_days) * 1.2
    activity_bonus = max(0, 14 - inactive_days) * 1.5
    issue_penalty = min(open_issues * 0.15, 15)

    return round(stars * 0.55 + forks * 0.2 + watchers * 0.15 + freshness_bonus + activity_bonus - issue_penalty, 2)


def analyze_payload(payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(UTC)
    items = payload.get("items", [])

    insights = [build_insight(repo, now) for repo in items]
    ranked = sorted(insights, key=lambda item: item.score, reverse=True)

    language_counter = Counter(item.language for item in insights if item.language)
    topic_counter = Counter(topic for item in insights for topic in item.topics)

    most_active = sorted(insights, key=lambda item: item.inactive_days)[:5]
    new_opportunities = sorted(insights, key=lambda item: (item.freshness_days, -item.score))[:5]

    return {
        "generated_at": now.isoformat(),
        "summary": {
            "total_repositories": len(insights),
            "top_language": language_counter.most_common(1)[0][0] if language_counter else "Unknown",
            "average_score": round(sum(item.score for item in insights) / len(insights), 2) if insights else 0,
        },
        "top_repositories": [asdict(item) for item in ranked[:10]],
        "language_distribution": dict(language_counter.most_common()),
        "topic_distribution": dict(topic_counter.most_common(15)),
        "most_active": [asdict(item) for item in most_active],
        "new_opportunities": [asdict(item) for item in new_opportunities],
    }


def build_insight(repo: dict[str, Any], now: datetime) -> RepoInsight:
    created_at = parse_iso_datetime(repo["created_at"])
    updated_at = parse_iso_datetime(repo["updated_at"])
    return RepoInsight(
        full_name=repo["full_name"],
        html_url=repo["html_url"],
        description=repo.get("description") or "",
        language=repo.get("language") or "Unknown",
        stars=repo.get("stargazers_count", 0),
        forks=repo.get("forks_count", 0),
        watchers=repo.get("watchers_count", 0),
        open_issues=repo.get("open_issues_count", 0),
        created_at=repo["created_at"],
        updated_at=repo["updated_at"],
        topics=repo.get("topics", []),
        score=compute_score(repo, now=now),
        freshness_days=max((now - created_at).days, 0),
        inactive_days=max((now - updated_at).days, 0),
    )


def parse_iso_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))
