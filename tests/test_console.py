from fastapi.testclient import TestClient


def test_console_has_semantic_start_flow(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert '<main id="main">' in response.text
    assert "operator_confirmed_disclosure" in client.get("/app.js").text
    assert "Skip to meetings" in response.text
