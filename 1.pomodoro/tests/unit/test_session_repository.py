from datetime import datetime, timezone

from pomodoro_app.models import SessionRecord
from pomodoro_app.repositories.session_repository import SessionRepository
from pomodoro_app.time_provider import TimeProvider


class FixedTimeProvider(TimeProvider):
    def __init__(self, current_time: datetime) -> None:
        self.current_time = current_time

    def now(self) -> datetime:
        return self.current_time


def test_list_today_returns_empty_collection_by_default(tmp_path) -> None:
    repository = SessionRepository(str(tmp_path / "test.sqlite3"))

    assert list(repository.list_today()) == []


def test_save_returns_the_same_session_record(tmp_path) -> None:
    repository = SessionRepository(str(tmp_path / "test.sqlite3"))
    session = SessionRecord(
        session_type="focus",
        duration_seconds=25 * 60,
        started_at=datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 4, 2, 9, 25, tzinfo=timezone.utc),
    )

    saved_session = repository.save(session)

    assert saved_session is session


def test_list_today_returns_only_sessions_completed_today(tmp_path) -> None:
    now = datetime(2026, 4, 2, 12, 0, tzinfo=timezone.utc)
    repository = SessionRepository(
        str(tmp_path / "test.sqlite3"),
        time_provider=FixedTimeProvider(now),
    )

    today_session = SessionRecord(
        session_type="focus",
        duration_seconds=25 * 60,
        started_at=datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 4, 2, 9, 25, tzinfo=timezone.utc),
    )
    previous_day_session = SessionRecord(
        session_type="focus",
        duration_seconds=25 * 60,
        started_at=datetime(2026, 4, 1, 9, 0, tzinfo=timezone.utc),
        completed_at=datetime(2026, 4, 1, 9, 25, tzinfo=timezone.utc),
    )

    repository.save(today_session)
    repository.save(previous_day_session)

    sessions = list(repository.list_today())

    assert len(sessions) == 1
    assert sessions[0].session_type == "focus"
    assert sessions[0].duration_seconds == 25 * 60