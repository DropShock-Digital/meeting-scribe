from __future__ import annotations

import json
from typing import Any

from .config import Settings
from .models import Meeting, MeetingStatus, now
from .store import Store

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

    def get(self, meeting_id: str) -> Meeting:
        meeting = self.store.get_meeting(meeting_id)
        if meeting is None:
            raise StateError("Meeting was not found.")
        return meeting

    def deliver_disclosure(self, meeting_id: str, delivery: str) -> Meeting:
        meeting = self.get(meeting_id)
        if meeting.status is not MeetingStatus.DISCLOSING:
            raise StateError("Disclosure can only be delivered before recording starts.")
        return self.store.transition(
            meeting,
            MeetingStatus.RECORDING,
            "disclosure.delivered",
            {"delivery": delivery[:80]},
            now(),
        )

    def acknowledge(self, meeting_id: str, participant_id: str) -> None:
        meeting = self.get(meeting_id)
        if meeting.status is MeetingStatus.FINALIZED:
            raise StateError("Meeting is finalized.")
        if not participant_id.strip():
            raise PolicyError("Participant identifier is required.")
        self.store.append_event(
            meeting.id,
            "consent.acknowledged",
            {"participant_id": participant_id.strip()[:200]},
            now(),
        )

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
        self.store.append_event(meeting.id, "transcript.segment", data, now())

    def warn(self, meeting_id: str, component: str, message: str) -> Meeting:
        meeting = self.get(meeting_id)
        if meeting.status is MeetingStatus.FINALIZED:
            raise StateError("Meeting is finalized.")
        return self.store.transition(
            meeting,
            MeetingStatus.DEGRADED,
            "system.warning",
            {"component": component[:80], "message": message[:500]},
            now(),
        )

    def finalize(self, meeting_id: str, reason: str) -> Meeting:
        meeting = self.get(meeting_id)
        if meeting.status is MeetingStatus.FINALIZED:
            return meeting
        return self.store.transition(
            meeting, MeetingStatus.FINALIZED, "meeting.finalized", {"reason": reason[:300]}, now()
        )

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
