from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _csv(name: str, default: str = "") -> frozenset[str]:
    return frozenset(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    data_dir: Path
    bind_host: str
    port: int
    channel_allowlist: frozenset[str]
    operator_allowlist: frozenset[str]
    max_transcript_chars: int
    discord_enabled: bool
    discord_token: str | None
    discord_guild_id: str | None

    @classmethod
    def from_env(cls) -> Settings:
        return cls(
            data_dir=Path(os.getenv("MEETING_SCRIBE_DATA_DIR", "./data")),
            bind_host=os.getenv("MEETING_SCRIBE_BIND_HOST", "127.0.0.1"),
            port=int(os.getenv("MEETING_SCRIBE_PORT", "8080")),
            channel_allowlist=_csv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "demo-room"),
            operator_allowlist=_csv("MEETING_SCRIBE_OPERATOR_ALLOWLIST", "local-demo"),
            max_transcript_chars=int(os.getenv("MEETING_SCRIBE_MAX_TRANSCRIPT_CHARS", "4000")),
            discord_enabled=_bool("MEETING_SCRIBE_DISCORD_ENABLED"),
            discord_token=os.getenv("MEETING_SCRIBE_DISCORD_TOKEN") or None,
            discord_guild_id=os.getenv("MEETING_SCRIBE_DISCORD_GUILD_ID") or None,
        )

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "exports").mkdir(exist_ok=True)

    @property
    def database_path(self) -> Path:
        return self.data_dir / "meeting-scribe.sqlite3"

    def channel_is_allowed(self, channel_id: str) -> bool:
        return channel_id in self.channel_allowlist

    def operator_is_allowed(self, operator_id: str) -> bool:
        return operator_id in self.operator_allowlist
