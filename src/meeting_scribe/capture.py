"""Audio capture capability boundaries.

The core service must never label a meeting as captured unless a concrete transport
reports a successful start. This module fails closed while the Discord DAVE voice
receive ecosystem lacks a verified implementation for this project.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CaptureCapability:
    adapter: str
    available: bool
    reason: str
    verification_required: tuple[str, ...]


DISCORD_CAPTURE_CAPABILITY = CaptureCapability(
    adapter="discord-voice-receive",
    available=False,
    reason=(
        "No Discord audio-receive implementation is enabled. Pycord 2.8.1 warns that "
        "voice reception is currently broken under Discord DAVE end-to-end encryption."
    ),
    verification_required=(
        "Use a dedicated non-sensitive test guild.",
        "Prove per-speaker capture, reconnect, stop, and failure events.",
        "Review the exact dependency's DAVE support and security posture.",
        "Record a successful opt-in end-to-end test before any live meeting.",
    ),
)


class CaptureUnavailableError(RuntimeError):
    pass


def require_discord_capture() -> None:
    """Raise instead of silently pretending Discord audio is being captured."""
    raise CaptureUnavailableError(DISCORD_CAPTURE_CAPABILITY.reason)
