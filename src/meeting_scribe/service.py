from __future__ import annotations

import json
from typing import Any

from .config import Settings
from .models import Meeting, MeetingStatus, now
from .store import StateConflictError, Store

DEFAULT_DISCLOSURE = (
    "This meeting is being recorded and summarized. Please leave now if you do not consent."
)


class PolicyError(ValueError):
    pass


class StateError(ValueError):
    pass


class MeetingService:
    def __init__(self, settings: Settings, store: Store) -> None:
        self.settings = settings
        self.store = store

    def create(
        self, *, title: str, channel_id: str, operator_id: str, disclosure: str, confirmed: bool
    ) -> Meeting:
        if not confirmed:
            raise PolicyError("Operator must explicitly confirm the recording disclosure.")
        if not self.settings.channel_is_allowed(channel_id):
            raise PolicyError("Channel is not allowlisted for recording.")
        if not self.settings.operator_is_allowed(operator_id):
            raise PolicyError("Operator is not authorized to start a meeting.")
        clean_title = title.strip()
        clean_disclosure = disclosure.strip()
        if not clean_title or not clean_disclosure:
            raise PolicyError("Title and disclosure are required.")
        meeting = Meeting.new(clean_title[:200], channel_id, operator_id, clean_disclosure[:1000])
        self.store.create_meeting(
            meeting, "meeting.created", {"operator_confirmed_disclosure": True}
        )
        return meeting

    def console_meeting(self, meeting: Meeting) -> dict[str, Any]:
        """Return operator-readable meeting state without configuration identifiers."""
        mode = "offline-review" if any(
            event.kind == "review.created" for event in self.store.list_events(meeting.id)
        ) else "meeting"
        return {
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "mode": mode,
            "created_at": meeting.created_at,
            "started_at": meeting.started_at,
            "finalized_at": meeting.finalized_at,
        }

    def create_offline_review(self) -> Meeting:
        """Create a clearly non-capturing record for console walkthroughs."""
        if not self.settings.channel_allowlist or not self.settings.operator_allowlist:
            raise PolicyError("Configure an approved room and operator before creating a review record.")
        created_at = now()
        stamp = created_at.split(".", 1)[0].replace("T", " ") + " UTC"
        meeting = Meeting.new(
            f"Private review · {stamp}",
            sorted(self.settings.channel_allowlist)[0],
            sorted(self.settings.operator_allowlist)[0],
            DEFAULT_DISCLOSURE,
        )
        self.store.create_meeting(
            meeting,
            "meeting.created",
            {"origin": "offline-review", "capture_requested": False},
        )
        self.store.append_event_if_status(
            meeting.id,
            (MeetingStatus.DISCLOSING,),
            "review.created",
            {"mode": "offline", "capture": "not-started"},
            now(),
        )
        return meeting

    def console_snapshot(self) -> dict[str, Any]:
        """Read model for the operator console; deliberately omits secrets and IDs."""
        meetings = self.store.list_meetings()
        active = [meeting for meeting in meetings if meeting.status is not MeetingStatus.FINALIZED]
        archived = [meeting for meeting in meetings if meeting.status is MeetingStatus.FINALIZED]
        return {
            "system": {
                "configured_room_count": len(self.settings.voice_rooms),
            },
            "rooms": [
                {"key": room.key, "label": room.label} for room in self.settings.voice_rooms
            ],
            "disclosure": DEFAULT_DISCLOSURE,
            "active": [self.console_meeting(meeting) for meeting in active],
            "archive": [self.console_meeting(meeting) for meeting in archived],
        }

    def get(self, meeting_id: str) -> Meeting:
        meeting = self.store.get_meeting(meeting_id)
        if meeting is None:
            raise StateError("Meeting was not found.")
        return meeting

    def deliver_disclosure(self, meeting_id: str, delivery: str) -> Meeting:
        """Record notice delivery without claiming audio capture has started.

        A future verified capture adapter must own the separate transition into
        ``recording``. The current Discord receive boundary is unavailable and
        must never be bypassed by a browser/API acknowledgement.
        """
        meeting = self.get(meeting_id)
        if meeting.status is not MeetingStatus.DISCLOSING:
            raise StateError("Disclosure can only be delivered before capture starts.")
        try:
            self.store.append_event_once_if_status(
                meeting.id,
                (MeetingStatus.DISCLOSING,),
                "disclosure.delivered",
                {"delivery": delivery[:80]},
                now(),
            )
            return meeting
        except StateConflictError as error:
            raise StateError("Meeting state changed; disclosure was not delivered twice.") from error

    def acknowledge(self, meeting_id: str, participant_id: str) -> None:
        meeting = self.get(meeting_id)
        if meeting.status is MeetingStatus.FINALIZED:
            raise StateError("Meeting is finalized.")
        if not participant_id.strip():
            raise PolicyError("Participant identifier is required.")
        try:
            self.store.append_event_if_status(
                meeting.id,
                (MeetingStatus.DISCLOSING, MeetingStatus.RECORDING, MeetingStatus.DEGRADED),
                "consent.acknowledged",
                {"participant_id": participant_id.strip()[:200]},
                now(),
            )
        except StateConflictError as error:
            raise StateError("Meeting state changed; acknowledgement was not added.") from error

    def transcript(
        self, meeting_id: str, text: str, source: str, speaker: str | None = None
    ) -> None:
        meeting = self.get(meeting_id)
        if meeting.status is not MeetingStatus.RECORDING:
            raise StateError("Transcript ingestion is only available while recording.")
        clean = text.strip()
        if not clean:
            raise PolicyError("Transcript text is required.")
        if len(clean) > self.settings.max_transcript_chars:
            raise PolicyError("Transcript segment exceeds the configured size limit.")
        data: dict[str, Any] = {"text": clean, "source": source.strip()[:80] or "unknown"}
        if speaker and speaker.strip():
            data["speaker"] = speaker.strip()[:200]
        try:
            self.store.append_event_if_status(
                meeting.id,
                (MeetingStatus.RECORDING,),
                "transcript.segment",
                data,
                now(),
            )
        except StateConflictError as error:
            raise StateError("Meeting state changed; transcript segment was not added.") from error

    def warn(self, meeting_id: str, component: str, message: str) -> Meeting:
        meeting = self.get(meeting_id)
        if meeting.status is MeetingStatus.FINALIZED:
            raise StateError("Meeting is finalized.")
        try:
            return self.store.transition(
                meeting,
                MeetingStatus.DEGRADED,
                "system.warning",
                {"component": component[:80], "message": message[:500]},
                now(),
            )
        except StateConflictError as error:
            raise StateError("Meeting state changed; warning was not applied.") from error

    def finalize(self, meeting_id: str, reason: str) -> Meeting:
        # A competing write can win between the read and conditional update. Retry
        # once with the fresh state so a requested finalization cannot resurrect a
        # stale status or silently disappear.
        for _ in range(2):
            meeting = self.get(meeting_id)
            if meeting.status is MeetingStatus.FINALIZED:
                return meeting
            try:
                return self.store.transition(
                    meeting,
                    MeetingStatus.FINALIZED,
                    "meeting.finalized",
                    {"reason": reason[:300]},
                    now(),
                )
            except StateConflictError:
                continue
        raise StateError("Meeting state changed repeatedly; finalization was not applied.")

    def detail(self, meeting_id: str) -> dict[str, Any]:
        meeting = self.get(meeting_id)
        return {
            "meeting": meeting.public(),
            "events": [event.public() for event in self.store.list_events(meeting.id)],
        }

    def export_markdown(self, meeting_id: str) -> str:
        detail = self.detail(meeting_id)
        meeting = detail["meeting"]
        lines = [
            f"# {meeting['title']}",
            "",
            "## Meeting record",
            f"- **Status:** {meeting['status']}",
            f"- **Channel:** {meeting['channel_id']}",
            f"- **Created:** {meeting['created_at']}",
            f"- **Disclosure:** {meeting['disclosure']}",
            "",
            "## Timeline",
        ]
        transcript_lines: list[str] = []
        for event in detail["events"]:
            data = event["data"]
            lines.append(f"- `{event['occurred_at']}` — **{event['kind']}**")
            if event["kind"] == "transcript.segment":
                speaker = f"**{data['speaker']}**: " if data.get("speaker") else ""
                transcript_lines.append(f"- `{event['occurred_at']}` {speaker}{data['text']}")
        lines.extend(
            [
                "",
                "## Transcript",
                *(transcript_lines or ["_No transcript segments were stored._"]),
                "",
            ]
        )
        return "\n".join(lines)

    def export_json(self, meeting_id: str) -> str:
        return json.dumps(self.detail(meeting_id), indent=2, sort_keys=True) + "\n"
