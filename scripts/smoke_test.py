#!/usr/bin/env python3
from __future__ import annotations

import os

from fastapi.testclient import TestClient

os.environ.setdefault("MEETING_SCRIBE_DATA_DIR", "/tmp/meeting-scribe-smoke")
os.environ.setdefault("MEETING_SCRIBE_CHANNEL_ALLOWLIST", "demo-room")
os.environ.setdefault("MEETING_SCRIBE_OPERATOR_ALLOWLIST", "local-demo")
from meeting_scribe.main import create_app

with TestClient(create_app()) as client:
    assert client.get("/api/health").json()["status"] == "ok"
    assert client.get("/").status_code == 200
print("Local smoke test passed.")
