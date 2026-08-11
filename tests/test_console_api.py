from fastapi.testclient import TestClient


def test_console_snapshot_hides_configuration_identifiers_and_reports_capture_boundary(
    client: TestClient,
) -> None:
    response = client.get("/api/console")
    assert response.status_code == 200
    payload = response.json()
    serialized = response.text
    assert payload["capture"]["available"] is False
    assert payload["system"]["configured_room_count"] == 1
    assert payload["capture"]["label"] == "Safely paused"
    assert payload["rooms"] == [{"key": "review-room", "label": "Demo room"}]
    assert {provider["key"] for provider in payload["providers"]} == {
        "codex-oauth", "openrouter", "lmstudio", "compatible"
    }
    assert all(provider["configured"] is False for provider in payload["providers"])
    assert "demo-room" not in serialized
    assert "local-demo" not in serialized
    assert "discord_token" not in serialized


def test_offline_review_uses_configured_identity_without_claiming_capture(client: TestClient) -> None:
    response = client.post("/api/meetings/offline-review")
    assert response.status_code == 201
    meeting = response.json()["meeting"]
    assert meeting["title"].startswith("Offline review ·")
    assert meeting["status"] == "disclosing"
    assert meeting["mode"] == "offline-review"
    assert "channel_id" not in meeting
    assert "requested_by" not in meeting

    detail = client.get(f"/api/meetings/{meeting['id']}").json()
    review_events = [event for event in detail["events"] if event["kind"] == "review.created"]
    assert review_events == [
        {
            "id": review_events[0]["id"],
            "meeting_id": meeting["id"],
            "kind": "review.created",
            "data": {"mode": "offline", "capture": "not-started"},
            "occurred_at": review_events[0]["occurred_at"],
        }
    ]
    assert client.post(
        f"/api/meetings/{meeting['id']}/transcript", json={"text": "not allowed", "source": "test"}
    ).status_code == 409


def test_console_sanitizes_named_room_and_configured_provider(tmp_path, monkeypatch) -> None:
    key_file = tmp_path / "openrouter-key"
    key_file.write_text("test-only-secret", encoding="utf-8")
    monkeypatch.setenv("MEETING_SCRIBE_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "123456789012345678")
    monkeypatch.setenv(
        "MEETING_SCRIBE_ROOM_CATALOG",
        '[{"key":"review-room","channel_id":"123456789012345678","label":"Review room"}]',
    )
    monkeypatch.setenv("MEETING_SCRIBE_OPENROUTER_API_KEY_FILE", str(key_file))
    from meeting_scribe.main import create_app

    with TestClient(create_app()) as configured_client:
        response = configured_client.get("/api/console")

    payload = response.json()
    serialized = response.text
    openrouter = next(provider for provider in payload["providers"] if provider["key"] == "openrouter")
    assert payload["rooms"] == [{"key": "review-room", "label": "Review room"}]
    assert openrouter["configured"] is True
    assert "123456789012345678" not in serialized
    assert "test-only-secret" not in serialized
    assert str(key_file) not in serialized
