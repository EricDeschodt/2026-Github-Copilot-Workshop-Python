from datetime import datetime, timezone

from pomodoro_app.models import SessionRecord
from pomodoro_app.services.stats_service import calculate_focus_minutes, summarize_today


def test_calculate_focus_minutes_counts_only_completed_focus_sessions() -> None:
    started_at = datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc)
    completed_at = datetime(2026, 4, 2, 9, 25, tzinfo=timezone.utc)

    sessions = [
        SessionRecord(
            session_type="focus",
            duration_seconds=25 * 60,
            started_at=started_at,
            completed_at=completed_at,
        ),
        SessionRecord(
            session_type="short_break",
            duration_seconds=5 * 60,
            started_at=started_at,
            completed_at=completed_at,
        ),
        SessionRecord(
            session_type="focus",
            duration_seconds=10 * 60,
            started_at=started_at,
            completed_at=None,
        ),
    ]

    assert calculate_focus_minutes(sessions) == 25


def test_calculate_focus_minutes_floors_partial_minutes() -> None:
    started_at = datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc)
    completed_at = datetime(2026, 4, 2, 9, 24, 59, tzinfo=timezone.utc)

    sessions = [
        SessionRecord(
            session_type="focus",
            duration_seconds=24 * 60 + 59,
            started_at=started_at,
            completed_at=completed_at,
        )
    ]

    assert calculate_focus_minutes(sessions) == 24


def test_calculate_focus_minutes_returns_zero_when_no_completed_focus_sessions() -> None:
    started_at = datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc)

    sessions = [
        SessionRecord(
            session_type="short_break",
            duration_seconds=5 * 60,
            started_at=started_at,
            completed_at=started_at,
        ),
        SessionRecord(
            session_type="focus",
            duration_seconds=25 * 60,
            started_at=started_at,
            completed_at=None,
        ),
    ]

    assert calculate_focus_minutes(sessions) == 0


def test_summarize_today_returns_focus_summary() -> None:
    started_at = datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc)
    completed_at = datetime(2026, 4, 2, 9, 25, tzinfo=timezone.utc)

    sessions = [
        SessionRecord(
            session_type="focus",
            duration_seconds=25 * 60,
            started_at=started_at,
            completed_at=completed_at,
        ),
        SessionRecord(
            session_type="short_break",
            duration_seconds=5 * 60,
            started_at=started_at,
            completed_at=completed_at,
        ),
    ]

    assert summarize_today(sessions) == {
        "sessions_completed": 1,
        "focus_minutes": 25,
        "current_streak": 1,
    }