from __future__ import annotations

import pytest

from meeting_scribe.config import Settings


def test_room_catalog_is_named_but_restricted_to_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "voice-123,voice-456")
    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG",
        '[{"key":"design-review","channel_id":"voice-123","label":"Design review"},'
        '{"key":"team-standup","channel_id":"voice-456","label":"Team standup"}]',
    )

    settings = Settings.from_env()

    assert [(room.key, room.label) for room in settings.voice_rooms] == [
        ("design-review", "Design review"),
        ("team-standup", "Team standup"),
    ]
    assert settings.voice_rooms[0].channel_id == "voice-123"


def test_room_catalog_refuses_a_room_outside_the_allowlist(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "voice-123")
    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG", '[{"key":"not-approved","channel_id":"voice-456","label":"Not approved"}]'
    )

    with pytest.raises(ValueError, match="allowlisted"):
        Settings.from_env()




def test_room_catalog_rejects_duplicate_labels_and_missing_stable_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "voice-123,voice-456")
    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG",
        '[{"key":"one-room","channel_id":"voice-123","label":"Planning"},'
        '{"key":"two-room","channel_id":"voice-456","label":"planning"}]',
    )

    with pytest.raises(ValueError, match="unique"):
        Settings.from_env()

    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG", '[{"channel_id":"voice-123","label":"Planning"}]'
    )
    with pytest.raises(ValueError, match="stable opaque key"):
        Settings.from_env()


def test_stable_room_key_survives_catalog_reordering(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "voice-123,voice-456")
    original = '[{"key":"design-review","channel_id":"voice-123","label":"Design review"},' \
        '{"key":"team-standup","channel_id":"voice-456","label":"Team standup"}]'
    reordered = '[{"key":"team-standup","channel_id":"voice-456","label":"Team standup"},' \
        '{"key":"design-review","channel_id":"voice-123","label":"Design review"}]'
    monkeypatch.setenv("MEETING_SCRIBE_ROOM_CATALOG", original)
    first = {room.key: room.label for room in Settings.from_env().voice_rooms}
    monkeypatch.setenv("MEETING_SCRIBE_ROOM_CATALOG", reordered)
    second = {room.key: room.label for room in Settings.from_env().voice_rooms}

    assert first == second == {"design-review": "Design review", "team-standup": "Team standup"}

def test_room_catalog_refuses_identifier_as_a_display_label(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "123456789012345678")
    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG",
        '[{"key":"test-room","channel_id":"123456789012345678","label":"123456789012345678"}]',
    )

    with pytest.raises(ValueError, match="human-readable label"):
        Settings.from_env()


def test_compatible_provider_refuses_endpoint_as_a_display_label(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MEETING_SCRIBE_COMPATIBLE_PROVIDER_LABEL", "https://provider.example/v1")

    with pytest.raises(ValueError, match="human-readable label"):
        Settings.from_env()


def test_provider_readiness_never_returns_secret_value(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    key_file = tmp_path / "provider-key"
    key_file.write_text("not-a-real-key", encoding="utf-8")
    monkeypatch.setenv("MEETING_SCRIBE_OPENROUTER_API_KEY_FILE", str(key_file))

    providers = Settings.from_env().ai_providers

    openrouter = next(provider for provider in providers if provider.key == "openrouter")
    assert openrouter.configured is True
    assert "not-a-real-key" not in openrouter.detail
    assert str(key_file) not in openrouter.detail


def test_provider_configuration_requires_a_nonempty_secret_file(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    empty_key_file = tmp_path / "empty-provider-key"
    empty_key_file.touch()
    monkeypatch.setenv("MEETING_SCRIBE_OPENROUTER_API_KEY_FILE", str(empty_key_file))

    providers = Settings.from_env().ai_providers
    openrouter = next(provider for provider in providers if provider.key == "openrouter")

    assert openrouter.configured is False
