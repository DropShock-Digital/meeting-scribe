from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("MEETING_SCRIBE_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "demo-room")
    monkeypatch.setenv("MEETING_SCRIBE_OPERATOR_ALLOWLIST", "local-demo")
    from meeting_scribe.main import create_app

    with TestClient(create_app()) as test_client:
        yield test_client
