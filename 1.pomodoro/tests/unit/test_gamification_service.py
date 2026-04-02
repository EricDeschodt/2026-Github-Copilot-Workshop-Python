from datetime import date, datetime, timezone

import pytest

from pomodoro_app.models import SessionRecord
from pomodoro_app.services.gamification_service import (
    build_daily_stats,
    calculate_level,
    calculate_streak,
    calculate_xp,
    count_total_focus_sessions,
    get_achievements,
)


def _focus(completed_at: datetime, duration: int = 25 * 60) -> SessionRecord:
    return SessionRecord(
        session_type="focus",
        duration_seconds=duration,
        started_at=completed_at,
        completed_at=completed_at,
    )


def _incomplete(completed_at: datetime | None = None) -> SessionRecord:
    return SessionRecord(
        session_type="focus",
        duration_seconds=25 * 60,
        started_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        completed_at=None,
    )


# --- calculate_xp ---

def test_calculate_xp_returns_zero_for_no_sessions() -> None:
    assert calculate_xp(0) == 0


def test_calculate_xp_awards_ten_per_session() -> None:
    assert calculate_xp(5) == 50


# --- calculate_level ---

def test_calculate_level_starts_at_one() -> None:
    assert calculate_level(0) == 1


def test_calculate_level_advances_at_100_xp() -> None:
    assert calculate_level(100) == 2
    assert calculate_level(199) == 2
    assert calculate_level(200) == 3


# --- calculate_streak ---

def test_calculate_streak_returns_zero_with_no_sessions() -> None:
    assert calculate_streak({}) == 0


def test_calculate_streak_counts_consecutive_days_from_today() -> None:
    today = datetime.now(timezone.utc).date()
    counts = {
        today: 2,
        today.replace(day=today.day - 1) if today.day > 1 else today: 1,
    }
    # Build a 3-day streak to avoid dependency on current date
    d0 = today
    d1 = date.fromordinal(today.toordinal() - 1)
    d2 = date.fromordinal(today.toordinal() - 2)
    daily_counts = {d0: 1, d1: 3, d2: 1}
    assert calculate_streak(daily_counts) == 3


def test_calculate_streak_stops_at_gap() -> None:
    today = datetime.now(timezone.utc).date()
    d0 = today
    d2 = date.fromordinal(today.toordinal() - 2)
    # Gap on d1 (yesterday)
    daily_counts = {d0: 1, d2: 1}
    assert calculate_streak(daily_counts) == 1


def test_calculate_streak_uses_yesterday_if_today_empty() -> None:
    today = datetime.now(timezone.utc).date()
    d1 = date.fromordinal(today.toordinal() - 1)
    d2 = date.fromordinal(today.toordinal() - 2)
    daily_counts = {d1: 2, d2: 1}
    assert calculate_streak(daily_counts) == 2


# --- count_total_focus_sessions ---

def test_count_total_focus_sessions_ignores_incomplete() -> None:
    sessions = [
        _focus(datetime(2026, 4, 1, tzinfo=timezone.utc)),
        _incomplete(),
    ]
    assert count_total_focus_sessions(sessions) == 1


def test_count_total_focus_sessions_ignores_breaks() -> None:
    sessions = [
        SessionRecord(
            session_type="short_break",
            duration_seconds=5 * 60,
            started_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
            completed_at=datetime(2026, 4, 1, tzinfo=timezone.utc),
        ),
    ]
    assert count_total_focus_sessions(sessions) == 0


# --- get_achievements ---

def test_get_achievements_first_pomodoro_unlocked_after_one_session() -> None:
    achievements = get_achievements(total_sessions=1, streak=0, today_sessions=1, weekly_sessions=1)
    first = next(a for a in achievements if a["id"] == "first_pomodoro")
    assert first["unlocked"] is True


def test_get_achievements_first_pomodoro_locked_with_zero_sessions() -> None:
    achievements = get_achievements(total_sessions=0, streak=0, today_sessions=0, weekly_sessions=0)
    first = next(a for a in achievements if a["id"] == "first_pomodoro")
    assert first["unlocked"] is False


def test_get_achievements_streak_3_unlocked() -> None:
    achievements = get_achievements(total_sessions=10, streak=3, today_sessions=0, weekly_sessions=5)
    streak_badge = next(a for a in achievements if a["id"] == "streak_3")
    assert streak_badge["unlocked"] is True


def test_get_achievements_week_champion_requires_10_weekly() -> None:
    achievements_not_enough = get_achievements(total_sessions=9, streak=0, today_sessions=0, weekly_sessions=9)
    achievements_enough = get_achievements(total_sessions=10, streak=0, today_sessions=0, weekly_sessions=10)
    champ_no = next(a for a in achievements_not_enough if a["id"] == "week_champion")
    champ_yes = next(a for a in achievements_enough if a["id"] == "week_champion")
    assert champ_no["unlocked"] is False
    assert champ_yes["unlocked"] is True


# --- build_daily_stats ---

def test_build_daily_stats_returns_correct_number_of_days() -> None:
    start = date(2026, 4, 1)
    result = build_daily_stats([], start, 7)
    assert len(result) == 7
    assert result[0]["date"] == "2026-04-01"
    assert result[6]["date"] == "2026-04-07"


def test_build_daily_stats_counts_completed_focus_sessions_per_day() -> None:
    start = date(2026, 4, 1)
    sessions = [
        _focus(datetime(2026, 4, 1, 10, 0, tzinfo=timezone.utc)),
        _focus(datetime(2026, 4, 1, 11, 0, tzinfo=timezone.utc)),
        _focus(datetime(2026, 4, 3, 9, 0, tzinfo=timezone.utc)),
    ]
    result = build_daily_stats(sessions, start, 3)
    assert result[0]["sessions_completed"] == 2
    assert result[1]["sessions_completed"] == 0
    assert result[2]["sessions_completed"] == 1
