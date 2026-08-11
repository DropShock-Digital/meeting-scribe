from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path


def _csv(name: str, default: str = "") -> frozenset[str]:
    return frozenset(item.strip() for item in os.getenv(name, default).split(",") if item.strip())


def _bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    return default if raw is None else raw.strip().lower() in {"1", "true", "yes", "on"}


_DISPLAY_ENDPOINT = re.compile(r"(?:https?://|www\.|discord(?:app)?\.com/|discord\.gg/)", re.IGNORECASE)
_DISCORD_SNOWFLAKE = re.compile(r"\b\d{15,21}\b")
_ROOM_KEY = re.compile(r"[a-z][a-z0-9-]{1,63}\Z")


def _display_label(value: str, *, field: str, channel_id: str | None = None) -> str:
    label = value.strip()
    if not label:
        raise ValueError(f"{field} must not be empty.")
    if label == channel_id or _DISPLAY_ENDPOINT.search(label) or _DISCORD_SNOWFLAKE.search(label):
        raise ValueError(f"{field} must be a human-readable label, not an identifier or endpoint.")
    return label[:100]


def _room_key(value: object) -> str:
    if not isinstance(value, str) or not _ROOM_KEY.fullmatch(value):
        raise ValueError("Each room catalog entry requires a stable opaque key.")
    return value


def _configured_secret_file(raw_path: str) -> bool:
    """Check a protected runtime-secret reference without reading or returning it.

    This is configuration status only. It is not provider authentication or health.
    """
    if not raw_path:
        return False
    path = Path(raw_path)
    try:
        return path.is_file() and path.stat().st_size > 0
    except OSError:
        return False


@dataclass(frozen=True)
class VoiceRoom:
    key: str
    channel_id: str
    label: str


@dataclass(frozen=True)
class AIProvider:
    key: str
    label: str
    detail: str
    configured: bool


def _room_catalog(allowlist: frozenset[str]) -> tuple[VoiceRoom, ...]:
    raw = os.getenv("MEETING_SCRIBE_ROOM_CATALOG", "").strip()
    if not raw:
        # An allowlist is an authorization boundary, not an operator-facing catalog.
        # A future gateway must not infer a human name or stable selector key from an ID.
        return ()
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ValueError("MEETING_SCRIBE_ROOM_CATALOG must be valid JSON.") from error
    if not isinstance(entries, list) or not entries:
        raise ValueError("MEETING_SCRIBE_ROOM_CATALOG must be a non-empty JSON list.")
    rooms: list[VoiceRoom] = []
    seen_ids: set[str] = set()
    seen_keys: set[str] = set()
    seen_labels: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("Each room catalog entry must be an object.")
        key = _room_key(entry.get("key"))
        channel_id = entry.get("channel_id")
        raw_label = entry.get("label")
        if not isinstance(channel_id, str) or not isinstance(raw_label, str):
            raise ValueError("Each room catalog entry requires string channel_id and label fields.")
        channel_id = channel_id.strip()
        label = _display_label(raw_label, field="Room label", channel_id=channel_id)
        normalized_label = label.casefold()
        if not channel_id:
            raise ValueError("Each room catalog entry requires channel_id and label.")
        if key == channel_id:
            raise ValueError("Room key must be opaque and distinct from channel_id.")
        if channel_id not in allowlist:
            raise ValueError("Every configured room must also be allowlisted.")
        if channel_id in seen_ids or key in seen_keys or normalized_label in seen_labels:
            raise ValueError("Configured rooms must have unique channels, keys, and labels.")
        seen_ids.add(channel_id)
        seen_keys.add(key)
        seen_labels.add(normalized_label)
        rooms.append(VoiceRoom(key, channel_id, label))
    return tuple(rooms)


def _ai_providers() -> tuple[AIProvider, ...]:
    openrouter_key_file = os.getenv("MEETING_SCRIBE_OPENROUTER_API_KEY_FILE", "").strip()
    openrouter_configured = _configured_secret_file(openrouter_key_file)
    codex_configured = _bool("MEETING_SCRIBE_CODEX_OAUTH_CONFIGURED")
    lmstudio_configured = _bool("MEETING_SCRIBE_LMSTUDIO_CONFIGURED")
    compatible_configured = _bool("MEETING_SCRIBE_COMPATIBLE_PROVIDER_CONFIGURED")
    compatible_label = _display_label(
        os.getenv("MEETING_SCRIBE_COMPATIBLE_PROVIDER_LABEL", "").strip() or "OpenAI-compatible",
        field="Compatible provider label",
    )
    return (
        AIProvider(
            "codex-oauth",
            "Codex OAuth",
            "Dedicated connection configuration required."
            if not codex_configured
            else "Configured for a future verified workflow; not verified or used yet.",
            codex_configured,
        ),
        AIProvider(
            "openrouter",
            "OpenRouter",
            "Protected runtime key source required."
            if not openrouter_configured
            else "Configured for a future verified workflow; not verified or used yet.",
            openrouter_configured,
        ),
        AIProvider(
            "lmstudio",
            "LM Studio",
            "Approved local endpoint configuration required."
            if not lmstudio_configured
            else "Configured for a future verified workflow; not verified or used yet.",
            lmstudio_configured,
        ),
        AIProvider(
            "compatible",
            compatible_label,
            "Approved compatible endpoint configuration required."
            if not compatible_configured
            else "Configured for a future verified workflow; not verified or used yet.",
            compatible_configured,
        ),
    )


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
    voice_rooms: tuple[VoiceRoom, ...]
    ai_providers: tuple[AIProvider, ...]

    @classmethod
    def from_env(cls) -> Settings:
        channel_allowlist = _csv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "demo-room")
        return cls(
            data_dir=Path(os.getenv("MEETING_SCRIBE_DATA_DIR", "./data")),
            bind_host=os.getenv("MEETING_SCRIBE_BIND_HOST", "127.0.0.1"),
            port=int(os.getenv("MEETING_SCRIBE_PORT", "8080")),
            channel_allowlist=channel_allowlist,
            operator_allowlist=_csv("MEETING_SCRIBE_OPERATOR_ALLOWLIST", "local-demo"),
            max_transcript_chars=int(os.getenv("MEETING_SCRIBE_MAX_TRANSCRIPT_CHARS", "4000")),
            discord_enabled=_bool("MEETING_SCRIBE_DISCORD_ENABLED"),
            discord_token=os.getenv("MEETING_SCRIBE_DISCORD_TOKEN") or None,
            discord_guild_id=os.getenv("MEETING_SCRIBE_DISCORD_GUILD_ID") or None,
            voice_rooms=_room_catalog(channel_allowlist),
            ai_providers=_ai_providers(),
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
