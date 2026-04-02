import sqlite3
from collections.abc import Iterable
from datetime import datetime, timedelta, timezone

from pomodoro_app.models import SessionRecord
from pomodoro_app.time_provider import TimeProvider


class SessionRepository:
    def __init__(self, db_path: str, time_provider: TimeProvider | None = None) -> None:
        self.db_path = db_path
        self.time_provider = time_provider or TimeProvider()
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_type TEXT NOT NULL,
                    duration_seconds INTEGER NOT NULL,
                    started_at TEXT NOT NULL,
                    completed_at TEXT
                )
                """
            )

    def list_today(self) -> Iterable[SessionRecord]:
        now = self.time_provider.now().astimezone(timezone.utc)
        start_of_day = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
        end_of_day = start_of_day + timedelta(days=1)

        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT session_type, duration_seconds, started_at, completed_at
                FROM sessions
                WHERE completed_at IS NOT NULL
                  AND completed_at >= ?
                  AND completed_at < ?
                ORDER BY completed_at ASC
                """,
                (start_of_day.isoformat(), end_of_day.isoformat()),
            ).fetchall()

        return [self._row_to_session(row) for row in rows]

    def save(self, session: SessionRecord) -> SessionRecord:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (session_type, duration_seconds, started_at, completed_at)
                VALUES (?, ?, ?, ?)
                """,
                (
                    session.session_type,
                    session.duration_seconds,
                    session.started_at.astimezone(timezone.utc).isoformat(),
                    session.completed_at.astimezone(timezone.utc).isoformat()
                    if session.completed_at is not None
                    else None,
                ),
            )

        return session

    @staticmethod
    def _row_to_session(row: sqlite3.Row) -> SessionRecord:
        completed_at = row["completed_at"]
        return SessionRecord(
            session_type=row["session_type"],
            duration_seconds=row["duration_seconds"],
            started_at=datetime.fromisoformat(row["started_at"]),
            completed_at=datetime.fromisoformat(completed_at) if completed_at else None,
        )