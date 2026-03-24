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


def compare_payloads(previous_payload: dict[str, Any], current_payload: dict[str, Any]) -> dict[str, Any]:
    previous_analysis = analyze_payload(previous_payload)
    current_analysis = analyze_payload(current_payload)

    previous_items = {repo["full_name"]: repo for repo in previous_payload.get("items", [])}
    current_items = {repo["full_name"]: repo for repo in current_payload.get("items", [])}

    previous_rank = build_rank_map(previous_analysis["top_repositories"])
    current_rank = build_rank_map(current_analysis["top_repositories"])

    new_entries = sorted(
        [
            build_change_entry(name, None, current_items[name], None, current_rank.get(name))
            for name in current_items
            if name not in previous_items
        ],
        key=lambda item: item["current_stars"],
        reverse=True,
    )

    star_movers = sorted(
        [
            build_change_entry(name, previous_items[name], current_items[name], previous_rank.get(name), current_rank.get(name))
            for name in current_items
            if name in previous_items
        ],
        key=lambda item: item["stars_delta"],
        reverse=True,
    )

    previous_languages = Counter(
        (repo.get("language") or "Unknown") for repo in previous_payload.get("items", [])
    )
    current_languages = Counter(
        (repo.get("language") or "Unknown") for repo in current_payload.get("items", [])
    )
    language_changes = []
    for language in sorted(set(previous_languages) | set(current_languages)):
        previous_count = previous_languages.get(language, 0)
        current_count = current_languages.get(language, 0)
        delta = current_count - previous_count
        if delta != 0:
            language_changes.append(
                {
                    "language": language,
                    "previous_count": previous_count,
                    "current_count": current_count,
                    "delta": delta,
                }
            )
    language_changes.sort(key=lambda item: abs(item["delta"]), reverse=True)

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "previous_summary": previous_analysis["summary"],
        "current_summary": current_analysis["summary"],
        "new_entries": new_entries[:10],
        "top_star_gainers": star_movers[:10],
        "top_rank_climbers": sorted(
            [item for item in star_movers if item["rank_delta"] is not None and item["rank_delta"] > 0],
            key=lambda item: item["rank_delta"],
            reverse=True,
        )[:10],
        "language_changes": language_changes[:10],
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


def build_rank_map(repositories: list[dict[str, Any]]) -> dict[str, int]:
    return {repo["full_name"]: index for index, repo in enumerate(repositories, start=1)}


def build_change_entry(
    full_name: str,
    previous_repo: dict[str, Any] | None,
    current_repo: dict[str, Any],
    previous_rank: int | None,
    current_rank: int | None,
) -> dict[str, Any]:
    previous_stars = previous_repo.get("stargazers_count", 0) if previous_repo else 0
    current_stars = current_repo.get("stargazers_count", 0)
    return {
        "full_name": full_name,
        "html_url": current_repo["html_url"],
        "language": current_repo.get("language") or "Unknown",
        "previous_stars": previous_stars,
        "current_stars": current_stars,
        "stars_delta": current_stars - previous_stars,
        "previous_rank": previous_rank,
        "current_rank": current_rank,
        "rank_delta": (previous_rank - current_rank) if previous_rank and current_rank else None,
    }
