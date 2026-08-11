from concurrent.futures import ThreadPoolExecutor
from threading import Barrier, Lock

import pytest
from fastapi.testclient import TestClient

from meeting_scribe.models import MeetingStatus
from meeting_scribe.service import StateError


def create_meeting(client: TestClient) -> str:
    response = client.post(
        "/api/meetings",
        json={
            "title": "Concurrent lifecycle test",
            "channel_id": "demo-room",
            "operator_id": "local-demo",
            "disclosure": "This meeting is recorded.",
            "operator_confirmed_disclosure": True,
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_disclosure_evidence_is_atomic_without_claiming_capture(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = client.app.state.service
    meeting_id = create_meeting(client)
    original_get = service.get
    barrier = Barrier(2)

    def synchronized_get(identifier: str):  # type: ignore[no-untyped-def]
        meeting = original_get(identifier)
        barrier.wait(timeout=5)
        return meeting

    monkeypatch.setattr(service, "get", synchronized_get)
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(service.deliver_disclosure, meeting_id, "test") for _ in range(2)]
        outcomes = [future.exception() for future in futures]
    monkeypatch.setattr(service, "get", original_get)

    assert sum(outcome is None for outcome in outcomes) == 1
    assert sum(isinstance(outcome, StateError) for outcome in outcomes) == 1
    detail = service.detail(meeting_id)
    assert detail["meeting"]["status"] == MeetingStatus.DISCLOSING
    assert [event["kind"] for event in detail["events"]].count("disclosure.delivered") == 1


def test_concurrent_finalize_never_allows_stale_disclosure_to_resurrect(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    service = client.app.state.service
    meeting_id = create_meeting(client)
    original_get = service.get
    barrier = Barrier(2)
    lock = Lock()
    reads = 0

    def synchronized_first_reads(identifier: str):  # type: ignore[no-untyped-def]
        nonlocal reads
        meeting = original_get(identifier)
        with lock:
            reads += 1
            synchronize = reads <= 2
        if synchronize:
            barrier.wait(timeout=5)
        return meeting

    monkeypatch.setattr(service, "get", synchronized_first_reads)
    with ThreadPoolExecutor(max_workers=2) as executor:
        disclosure = executor.submit(service.deliver_disclosure, meeting_id, "test")
        finalization = executor.submit(service.finalize, meeting_id, "operator-requested")
        outcomes = [disclosure.exception(), finalization.exception()]
    monkeypatch.setattr(service, "get", original_get)

    assert outcomes[1] is None
    assert outcomes[0] is None or isinstance(outcomes[0], StateError)
    detail = service.detail(meeting_id)
    assert detail["meeting"]["status"] == MeetingStatus.FINALIZED
    assert [event["kind"] for event in detail["events"]].count("meeting.finalized") == 1
    assert [event["kind"] for event in detail["events"]].count("disclosure.delivered") <= 1
