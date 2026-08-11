from fastapi.testclient import TestClient


def test_console_uses_human_language_and_avoids_configuration_form_fields(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert '<main id="control-room">' in response.text
    assert "Private reviews,<br><em>not recordings." in response.text
    assert "Start a private review" in response.text
    assert "Room to use next" in response.text
    assert "Meeting helper" in response.text
    assert "Recording is not available." in response.text
    assert "This version cannot join calls or record sound." in response.text
    assert "No meeting helper is available in this version." in response.text
    assert "See participant notice" in response.text
    assert "Channel ID" not in response.text
    assert "Operator ID" not in response.text
    assert "operator_confirmed_disclosure" not in response.text
    assert "Create offline review record" not in response.text
    assert "Control room" not in response.text
    assert "Next voice room" not in response.text
    assert "AI provider" not in response.text
    assert 'type="password"' not in response.text
    assert "API key" not in response.text


def test_console_script_uses_sanitized_human_read_model(client: TestClient) -> None:
    script = client.get("/app.js").text
    assert "'/api/console'" in script
    assert "/api/meetings/offline-review" in script
    assert "channel_id" not in script
    assert "operator_id" not in script
    assert "localStorage" in script
    assert "Saved only in this browser. Nothing has started." in script
    assert "Private reviews,<br><em>not recordings.</em>" in script
    assert "Recording is not available." in script
    assert "No helper available." in script
    assert "Required before any future recording" in script
    assert "Open full record" in script
    assert "does not join a call or record sound" in script
    assert "Set up and" not in script
    assert "Recording available" not in script
    assert "needs setup" not in script
    assert "Download record" not in script
    assert "encrypted Discord receive path" not in script
    assert "Open Markdown" not in script
    assert "Open JSON" not in script
