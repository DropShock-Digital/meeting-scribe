from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import Event, Meeting, MeetingStatus


class Store:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS meetings (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, channel_id TEXT NOT NULL,
                    requested_by TEXT NOT NULL, disclosure TEXT NOT NULL, status TEXT NOT NULL,
                    created_at TEXT NOT NULL, started_at TEXT, finalized_at TEXT
                );
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, meeting_id TEXT NOT NULL,
                    kind TEXT NOT NULL, data_json TEXT NOT NULL, occurred_at TEXT NOT NULL,
                    FOREIGN KEY(meeting_id) REFERENCES meetings(id)
                );
                CREATE INDEX IF NOT EXISTS events_meeting_id_idx ON events(meeting_id, id);
                """
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        return connection

    def create_meeting(self, meeting: Meeting, event_kind: str, event_data: dict[str, Any]) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO meetings VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    meeting.id,
                    meeting.title,
                    meeting.channel_id,
                    meeting.requested_by,
                    meeting.disclosure,
                    meeting.status.value,
                    meeting.created_at,
                    meeting.started_at,
                    meeting.finalized_at,
                ),
            )
            self._append(connection, meeting.id, event_kind, event_data, meeting.created_at)

    def get_meeting(self, meeting_id: str) -> Meeting | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM meetings WHERE id = ?", (meeting_id,)
            ).fetchone()
        return self._meeting(row) if row else None

    def list_meetings(self) -> list[Meeting]:
        with self._connect() as connection:
            rows = connection.execute("SELECT * FROM meetings ORDER BY created_at DESC").fetchall()
        return [self._meeting(row) for row in rows]

    def list_events(self, meeting_id: str) -> list[Event]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM events WHERE meeting_id = ? ORDER BY id", (meeting_id,)
            ).fetchall()
        return [
            Event(
                row["id"],
                row["meeting_id"],
                row["kind"],
                json.loads(row["data_json"]),
                row["occurred_at"],
            )
            for row in rows
        ]

    def transition(
        self,
        meeting: Meeting,
        status: MeetingStatus,
        event_kind: str,
        event_data: dict[str, Any],
        occurred_at: str,
    ) -> Meeting:
        started_at = (
            meeting.started_at
            if status not in {MeetingStatus.RECORDING, MeetingStatus.DEGRADED}
            else (meeting.started_at or occurred_at)
        )
        finalized_at = occurred_at if status is MeetingStatus.FINALIZED else meeting.finalized_at
        with self._connect() as connection:
            connection.execute(
                "UPDATE meetings SET status = ?, started_at = ?, finalized_at = ? WHERE id = ?",
                (status.value, started_at, finalized_at, meeting.id),
            )
            self._append(connection, meeting.id, event_kind, event_data, occurred_at)
        return Meeting(
            meeting.id,
            meeting.title,
            meeting.channel_id,
            meeting.requested_by,
            meeting.disclosure,
            status,
            meeting.created_at,
            started_at,
            finalized_at,
        )

    def append_event(
        self, meeting_id: str, kind: str, data: dict[str, Any], occurred_at: str
    ) -> None:
        with self._connect() as connection:
            self._append(connection, meeting_id, kind, data, occurred_at)

    @staticmethod
    def _append(
        connection: sqlite3.Connection,
        meeting_id: str,
        kind: str,
        data: dict[str, Any],
        occurred_at: str,
    ) -> None:
        connection.execute(
            "INSERT INTO events (meeting_id, kind, data_json, occurred_at) VALUES (?, ?, ?, ?)",
            (meeting_id, kind, json.dumps(data, sort_keys=True), occurred_at),
        )

    @staticmethod
    def _meeting(row: sqlite3.Row) -> Meeting:
        return Meeting(
            row["id"],
            row["title"],
            row["channel_id"],
            row["requested_by"],
            row["disclosure"],
            MeetingStatus(row["status"]),
            row["created_at"],
            row["started_at"],
            row["finalized_at"],
        )
