
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Database URL: mysql+pymysql://user:pass@host:port/dbname
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./fake_news.db")

    # Admin credentials (for demo). In production, use a proper identity provider.
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@example.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    # Suspicious phrase list for explainability
    SUSPICIOUS_PHRASES: list[str] = (
        "miracle cure",
        "breaking secret",
        "suppressed by",
        "shocking truth",
        "eliminates all",
        "cure all",
        "you won\'t believe",
        "secret government",
        "big pharma",
        "overnight results",
    )


settings = Settings()
