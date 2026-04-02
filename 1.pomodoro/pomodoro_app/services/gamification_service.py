from collections.abc import Sequence
from datetime import date, datetime, timedelta, timezone
from typing import TypedDict

from pomodoro_app.models import SessionRecord


XP_PER_SESSION = 10
XP_PER_LEVEL = 100


class Achievement(TypedDict):
    id: str
    name: str
    description: str
    unlocked: bool


class DayStat(TypedDict):
    date: str
    sessions_completed: int


_ACHIEVEMENTS: list[tuple[str, str, str]] = [
    ("first_pomodoro", "First Steps", "Complete your first Pomodoro"),
    ("five_in_a_day", "On a Roll", "Complete 5 Pomodoros in a single day"),
    ("ten_total", "Getting Serious", "Complete 10 Pomodoros in total"),
    ("fifty_total", "Dedicated", "Complete 50 Pomodoros in total"),
    ("streak_3", "Habit Forming", "Maintain a 3-day streak"),
    ("streak_7", "Week Warrior", "Maintain a 7-day streak"),
    ("week_champion", "Weekly Champion", "Complete 10 Pomodoros in one week"),
]


def calculate_xp(total_sessions: int) -> int:
    return total_sessions * XP_PER_SESSION


def calculate_level(xp: int) -> int:
    return xp // XP_PER_LEVEL + 1


def calculate_streak(daily_counts: dict[date, int]) -> int:
    today = datetime.now(timezone.utc).date()
    streak = 0
    current = today if daily_counts.get(today, 0) > 0 else today - timedelta(days=1)

    while daily_counts.get(current, 0) > 0:
        streak += 1
        current -= timedelta(days=1)

    return streak


def get_achievements(
    total_sessions: int,
    streak: int,
    today_sessions: int,
    weekly_sessions: int,
) -> list[Achievement]:
    results: list[Achievement] = []

    conditions: dict[str, bool] = {
        "first_pomodoro": total_sessions >= 1,
        "five_in_a_day": today_sessions >= 5,
        "ten_total": total_sessions >= 10,
        "fifty_total": total_sessions >= 50,
        "streak_3": streak >= 3,
        "streak_7": streak >= 7,
        "week_champion": weekly_sessions >= 10,
    }

    for achievement_id, name, description in _ACHIEVEMENTS:
        results.append(
            Achievement(
                id=achievement_id,
                name=name,
                description=description,
                unlocked=conditions.get(achievement_id, False),
            )
        )

    return results


def build_daily_stats(
    sessions: Sequence[SessionRecord],
    start: date,
    num_days: int,
) -> list[DayStat]:
    counts: dict[date, int] = {}
    for session in sessions:
        if session.session_type == "focus" and session.completed_at is not None:
            day = session.completed_at.astimezone(timezone.utc).date()
            counts[day] = counts.get(day, 0) + 1

    return [
        DayStat(
            date=str(start + timedelta(days=i)),
            sessions_completed=counts.get(start + timedelta(days=i), 0),
        )
        for i in range(num_days)
    ]


def count_total_focus_sessions(sessions: Sequence[SessionRecord]) -> int:
    return sum(
        1
        for session in sessions
        if session.session_type == "focus" and session.completed_at is not None
    )
