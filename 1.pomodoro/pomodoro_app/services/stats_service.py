from collections.abc import Iterable

from pomodoro_app.models import SessionRecord


def calculate_focus_minutes(sessions: Iterable[SessionRecord]) -> int:
    total_seconds = sum(
        session.duration_seconds
        for session in sessions
        if session.session_type == "focus" and session.completed_at is not None
    )
    return total_seconds // 60


def summarize_today(sessions: Iterable[SessionRecord]) -> dict[str, int]:
    session_list = list(sessions)
    completed_focus_sessions = [
        session
        for session in session_list
        if session.session_type == "focus" and session.is_completed
    ]

    return {
        "sessions_completed": len(completed_focus_sessions),
        "focus_minutes": calculate_focus_minutes(session_list),
        "current_streak": len(completed_focus_sessions),
    }