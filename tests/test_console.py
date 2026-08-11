from fastapi.testclient import TestClient


def test_console_is_operator_native_and_avoids_configuration_form_fields(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert '<main id="control-room">' in response.text
    assert "Control room" in response.text
    assert "Create offline review record" in response.text
    assert "Channel ID" not in response.text
    assert "Operator ID" not in response.text
    assert "operator_confirmed_disclosure" not in response.text
    assert "Skip to control room" in response.text


def test_console_script_uses_sanitized_console_read_model(client: TestClient) -> None:
    script = client.get("/app.js").text
    assert "'/api/console'" in script
    assert "/api/meetings/offline-review" in script
    assert "channel_id" not in script
    assert "operator_id" not in script
