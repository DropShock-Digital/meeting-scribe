from meeting_scribe.capture import (
    DISCORD_CAPTURE_CAPABILITY,
    CaptureUnavailableError,
    require_discord_capture,
)


def test_discord_capture_fails_closed_until_compatibility_is_verified() -> None:
    assert DISCORD_CAPTURE_CAPABILITY.available is False
    assert "DAVE" in DISCORD_CAPTURE_CAPABILITY.reason
    try:
        require_discord_capture()
    except CaptureUnavailableError as error:
        assert "No Discord audio-receive implementation" in str(error)
    else:
        raise AssertionError("Discord capture must fail closed, not claim a false recording.")
