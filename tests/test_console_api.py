from fastapi.testclient import TestClient


def test_console_snapshot_hides_configuration_identifiers_and_reports_capture_boundary(
    client: TestClient,
) -> None:
    response = client.get("/api/console")
    assert response.status_code == 200
    payload = response.json()
    serialized = response.text
    assert payload["capture"]["available"] is False
    assert payload["capture"]["label"] == "Safely paused"
    assert payload["system"]["configured_room_count"] == 1
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
