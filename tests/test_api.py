from fastapi.testclient import TestClient


def create(client: TestClient) -> str:
    response = client.post(
        "/api/meetings",
        json={
            "title": "Planning",
            "channel_id": "demo-room",
            "operator_id": "local-demo",
            "disclosure": "This meeting is recorded.",
            "operator_confirmed_disclosure": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_health_never_exposes_configuration_secrets(client: TestClient) -> None:
    assert client.get("/api/health").json() == {"status": "ok"}
    body = client.get("/api/configuration").json()
    serialized = client.get("/api/configuration").text
    assert "discord_token" not in body
    assert "demo-room" not in serialized
    assert "local-demo" not in serialized
    assert body["rooms"] == [{"key": "review-room", "label": "Demo room"}]


def test_creation_requires_explicit_confirmation_and_allowlists(client: TestClient) -> None:
    missing_confirmation = client.post(
        "/api/meetings",
        json={
            "title": "x",
            "channel_id": "demo-room",
            "operator_id": "local-demo",
            "disclosure": "notice",
            "operator_confirmed_disclosure": False,
        },
    )
    denied_channel = client.post(
        "/api/meetings",
        json={
            "title": "x",
            "channel_id": "not-allowed",
            "operator_id": "local-demo",
            "disclosure": "notice",
            "operator_confirmed_disclosure": True,
        },
    )
    assert missing_confirmation.status_code == 403
    assert denied_channel.status_code == 403
    assert client.get("/api/meetings").json() == []


def test_disclosure_evidence_never_claims_capture_without_verified_transport(client: TestClient) -> None:
    meeting_id = create(client)
    disclosure = client.post(f"/api/meetings/{meeting_id}/disclosure-delivered", json={"delivery": "test"})
    assert disclosure.status_code == 200
    assert disclosure.json()["status"] == "disclosing"
    detail = client.get(f"/api/meetings/{meeting_id}").json()
    assert [event["kind"] for event in detail["events"]] == [
        "meeting.created",
        "disclosure.delivered",
    ]
    assert (
        client.post(
            f"/api/meetings/{meeting_id}/transcript", json={"text": "too soon", "source": "test"}
        ).status_code
        == 409
    )
    assert (
        client.post(
            f"/api/meetings/{meeting_id}/acknowledgements", json={"participant_id": "alex"}
        ).status_code
        == 204
    )
    final = client.post(f"/api/meetings/{meeting_id}/finalize", json={"reason": "done"})
    assert final.status_code == 200
    assert final.json()["status"] == "finalized"
    assert (
        client.post(
            f"/api/meetings/{meeting_id}/transcript", json={"text": "late", "source": "test"}
        ).status_code
        == 409
    )


def test_exports_are_deterministic_and_include_disclosure_evidence(client: TestClient) -> None:
    meeting_id = create(client)
    client.post(f"/api/meetings/{meeting_id}/disclosure-delivered", json={"delivery": "test"})
    markdown = client.get(f"/api/meetings/{meeting_id}/export.md")
    payload = client.get(f"/api/meetings/{meeting_id}/export.json")
    assert markdown.status_code == 200 and "Disclosure:" in markdown.text
    assert payload.status_code == 200 and "disclosure.delivered" in payload.text
