from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data" / "raw"
REPORTS_DIR = PROJECT_ROOT / "reports"


@dataclass(slots=True)
class Settings:
    github_token: str | None
    api_base_url: str = "https://api.github.com"
    user_agent: str = "gh-hotspot-analyzer/0.1.0"


def load_dotenv_file(dotenv_path: Path | None = None) -> None:
    dotenv_file = dotenv_path or PROJECT_ROOT / ".env"
    if not dotenv_file.exists():
        return

    for line in dotenv_file.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())


def get_settings() -> Settings:
    load_dotenv_file()
    return Settings(github_token=os.getenv("GITHUB_TOKEN"))

