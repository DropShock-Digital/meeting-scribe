from __future__ import annotations

from typing import Any, NoReturn

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from .service import DEFAULT_DISCLOSURE, MeetingService, PolicyError, StateError

router = APIRouter(prefix="/api")


def service(request: Request) -> MeetingService:
    return request.app.state.service  # type: ignore[no-any-return]


def fail(error: Exception) -> NoReturn:
    if isinstance(error, PolicyError):
        raise HTTPException(status_code=403, detail=str(error)) from error
    if isinstance(error, StateError):
        raise HTTPException(status_code=409, detail=str(error)) from error
    raise error


class CreateMeeting(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    channel_id: str = Field(min_length=1, max_length=200)
    operator_id: str = Field(min_length=1, max_length=200)
    disclosure: str = Field(default=DEFAULT_DISCLOSURE, min_length=1, max_length=1000)
    operator_confirmed_disclosure: bool


class Disclosure(BaseModel):
    delivery: str = Field(default="operator-console", min_length=1, max_length=80)


class Acknowledgement(BaseModel):
    participant_id: str = Field(min_length=1, max_length=200)


class Transcript(BaseModel):
    text: str = Field(min_length=1)
    source: str = Field(default="manual-import", min_length=1, max_length=80)
    speaker: str | None = Field(default=None, max_length=200)


class WarningPayload(BaseModel):
    component: str = Field(min_length=1, max_length=80)
    message: str = Field(min_length=1, max_length=500)


class Finalize(BaseModel):
    reason: str = Field(default="operator-stopped", min_length=1, max_length=300)


@router.get("/health")
def health(request: Request) -> dict[str, str]:
    _ = service(request)
    return {"status": "ok"}


@router.get("/configuration")
def configuration(request: Request) -> dict[str, Any]:
    settings = request.app.state.settings
    return {
        "discord_enabled": settings.discord_enabled,
        "allowlisted_channel_count": len(settings.channel_allowlist),
        "allowlisted_operator_count": len(settings.operator_allowlist),
        "max_transcript_chars": settings.max_transcript_chars,
    }


@router.get("/console")
def console(request: Request) -> dict[str, Any]:
    return service(request).console_snapshot()


@router.get("/meetings")
def list_meetings(request: Request) -> list[dict[str, Any]]:
    return [meeting.public() for meeting in service(request).store.list_meetings()]


@router.post("/meetings", status_code=201)
def create_meeting(payload: CreateMeeting, request: Request) -> dict[str, Any]:
    try:
        return (
            service(request)
            .create(
                title=payload.title,
                channel_id=payload.channel_id,
                operator_id=payload.operator_id,
                disclosure=payload.disclosure,
                confirmed=payload.operator_confirmed_disclosure,
            )
            .public()
        )
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/offline-review", status_code=201)
def create_offline_review(request: Request) -> dict[str, Any]:
    try:
        meeting = service(request).create_offline_review()
        return {"meeting": service(request).console_meeting(meeting)}
    except (PolicyError, StateError) as error:
        fail(error)


@router.get("/meetings/{meeting_id}")
def meeting_detail(meeting_id: str, request: Request) -> dict[str, Any]:
    try:
        return service(request).detail(meeting_id)
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/{meeting_id}/disclosure-delivered")
def disclosure_delivered(meeting_id: str, payload: Disclosure, request: Request) -> dict[str, Any]:
    try:
        return service(request).deliver_disclosure(meeting_id, payload.delivery).public()
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/{meeting_id}/acknowledgements", status_code=204)
def acknowledge(meeting_id: str, payload: Acknowledgement, request: Request) -> None:
    try:
        service(request).acknowledge(meeting_id, payload.participant_id)
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/{meeting_id}/transcript", status_code=204)
def transcript(meeting_id: str, payload: Transcript, request: Request) -> None:
    try:
        service(request).transcript(meeting_id, payload.text, payload.source, payload.speaker)
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/{meeting_id}/warnings")
def warning(meeting_id: str, payload: WarningPayload, request: Request) -> dict[str, Any]:
    try:
        return service(request).warn(meeting_id, payload.component, payload.message).public()
    except (PolicyError, StateError) as error:
        fail(error)


@router.post("/meetings/{meeting_id}/finalize")
def finalize(meeting_id: str, payload: Finalize, request: Request) -> dict[str, Any]:
    try:
        return service(request).finalize(meeting_id, payload.reason).public()
    except (PolicyError, StateError) as error:
        fail(error)


@router.get("/meetings/{meeting_id}/export.md", response_class=PlainTextResponse)
def export_markdown(meeting_id: str, request: Request) -> str:
    try:
        return service(request).export_markdown(meeting_id)
    except (PolicyError, StateError) as error:
        fail(error)


@router.get("/meetings/{meeting_id}/export.json", response_class=PlainTextResponse)
def export_json(meeting_id: str, request: Request) -> str:
    try:
        return service(request).export_json(meeting_id)
    except (PolicyError, StateError) as error:
        fail(error)
