from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4


class MeetingStatus(StrEnum):
    DISCLOSING = "disclosing"
    RECORDING = "recording"
    DEGRADED = "degraded"
    FINALIZED = "finalized"


@dataclass(frozen=True)
class Meeting:
    id: str
    title: str
    channel_id: str
    requested_by: str
    disclosure: str
    status: MeetingStatus
    created_at: str
    started_at: str | None
    finalized_at: str | None

    @classmethod
    def new(cls, title: str, channel_id: str, requested_by: str, disclosure: str) -> Meeting:
        return cls(
            id=str(uuid4()),
            title=title,
            channel_id=channel_id,
            requested_by=requested_by,
            disclosure=disclosure,
            status=MeetingStatus.DISCLOSING,
            created_at=now(),
            started_at=None,
            finalized_at=None,
        )

    def public(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Event:
    id: int
    meeting_id: str
    kind: str
    data: dict[str, Any]
    occurred_at: str

    def public(self) -> dict[str, Any]:
        return asdict(self)


def now() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")
