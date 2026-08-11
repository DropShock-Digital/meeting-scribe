import sys
from pathlib import Path

from meeting_scribe import cli


def test_discord_subcommand_initializes_the_shared_service(
    monkeypatch, tmp_path: Path
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("MEETING_SCRIBE_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("MEETING_SCRIBE_DISCORD_ENABLED", "true")
    monkeypatch.setattr(sys, "argv", ["meeting-scribe", "discord"])
    captured = {}

    def fake_run(settings, service) -> None:  # type: ignore[no-untyped-def]
        captured["settings"] = settings
        captured["service"] = service

    monkeypatch.setattr(cli, "run_discord_adapter", fake_run)
    cli.main()

    assert captured["settings"].discord_enabled is True
    assert captured["service"].store.database_path.exists()
