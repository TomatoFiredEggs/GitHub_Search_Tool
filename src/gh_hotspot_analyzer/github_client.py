from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .config import DATA_DIR, get_settings


@dataclass(slots=True)
class FetchOptions:
    days: int = 30
    limit: int = 30
    sort: str = "stars"
    order: str = "desc"


class GitHubClient:
    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.api_base_url
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": settings.user_agent,
        }
        if settings.github_token:
            self.headers["Authorization"] = f"Bearer {settings.github_token}"

    def fetch_hot_repositories(self, options: FetchOptions) -> dict:
        created_after = (datetime.now(UTC) - timedelta(days=options.days)).date().isoformat()
        query = f"created:>{created_after} stars:>20 archived:false"
        per_page = min(options.limit, 100)

        params = urlencode(
            {
                "q": query,
                "sort": options.sort,
                "order": options.order,
                "per_page": per_page,
            }
        )
        request = Request(
            url=f"{self.base_url}/search/repositories?{params}",
            headers=self.headers,
        )
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"GitHub API request failed with status {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"GitHub API request failed: {exc.reason}") from exc

        payload["fetched_at"] = datetime.now(UTC).isoformat()
        payload["query_meta"] = {
            "days": options.days,
            "limit": options.limit,
            "sort": options.sort,
            "order": options.order,
            "query": query,
        }
        return payload


def save_payload(payload: dict, output_path: str | Path | None = None) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    target = Path(output_path) if output_path else DATA_DIR / default_filename()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return target


def load_payload(input_path: str | Path) -> dict:
    return json.loads(Path(input_path).read_text(encoding="utf-8"))


def default_filename() -> str:
    return f"github_hotspot_{datetime.now(UTC).strftime('%Y%m%d_%H%M%S')}.json"
