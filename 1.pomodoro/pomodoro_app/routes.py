from datetime import date, datetime, timedelta, timezone

from flask import Blueprint, current_app, jsonify, render_template, request

from .models import SessionRecord
from .services import (
    TimerConfig,
    build_daily_stats,
    calculate_level,
    calculate_streak,
    calculate_xp,
    count_total_focus_sessions,
    get_achievements,
    summarize_today,
)


main_blueprint = Blueprint("main", __name__)


@main_blueprint.get("/")
def index() -> str:
    return render_template("index.html")


@main_blueprint.get("/api/config")
def get_config():
    timer_config: TimerConfig = current_app.config["TIMER_CONFIG"]

    return jsonify(
        {
            "focus_seconds": timer_config.focus_seconds,
            "short_break_seconds": timer_config.short_break_seconds,
            "long_break_seconds": timer_config.long_break_seconds,
            "sessions_before_long_break": timer_config.sessions_before_long_break,
        }
    )


@main_blueprint.get("/api/stats/today")
def get_today_stats():
    repository = current_app.extensions["session_repository"]
    return jsonify(summarize_today(repository.list_today()))


@main_blueprint.post("/api/sessions")
def create_session():
    payload = request.get_json(silent=True) or {}

    required_fields = {"session_type", "duration_seconds", "started_at", "completed_at"}
    missing_fields = sorted(required_fields - payload.keys())
    if missing_fields:
        return jsonify({"error": "Missing required fields", "fields": missing_fields}), 400

    session_type = payload["session_type"]
    if session_type not in {"focus", "short_break", "long_break"}:
        return jsonify({"error": "Invalid session_type"}), 400

    try:
        duration_seconds = int(payload["duration_seconds"])
        started_at = datetime.fromisoformat(payload["started_at"])
        completed_at = datetime.fromisoformat(payload["completed_at"])
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid session payload"}), 400

    session = SessionRecord(
        session_type=session_type,
        duration_seconds=duration_seconds,
        started_at=started_at,
        completed_at=completed_at,
    )

    repository = current_app.extensions["session_repository"]
    repository.save(session)

    return jsonify({"status": "created"}), 201


@main_blueprint.get("/api/stats/gamification")
def get_gamification_stats():
    repository = current_app.extensions["session_repository"]
    now = datetime.now(timezone.utc)
    today_date = now.date()
    start_date = today_date - timedelta(days=89)
    start_of_range = datetime(start_date.year, start_date.month, start_date.day, tzinfo=timezone.utc)

    all_sessions = list(repository.list_range(start_of_range, now + timedelta(days=1)))
    today_list = list(repository.list_today())

    today_focus = sum(
        1 for s in today_list if s.session_type == "focus" and s.completed_at is not None
    )
    total_focus = count_total_focus_sessions(all_sessions)

    num_days = (today_date - start_date).days + 1
    daily = build_daily_stats(all_sessions, start_date, num_days)
    daily_counts: dict[date, int] = {
        date.fromisoformat(d["date"]): d["sessions_completed"]
        for d in daily
    }
    streak = calculate_streak(daily_counts)

    week_start = today_date - timedelta(days=6)
    weekly_sessions = sum(
        d["sessions_completed"]
        for d in daily
        if date.fromisoformat(d["date"]) >= week_start
    )

    xp = calculate_xp(total_focus)
    level = calculate_level(xp)
    achievements = get_achievements(total_focus, streak, today_focus, weekly_sessions)

    return jsonify(
        {
            "xp": xp,
            "level": level,
            "xp_for_next_level": 100 - (xp % 100),
            "streak": streak,
            "total_sessions": total_focus,
            "achievements": achievements,
        }
    )


@main_blueprint.get("/api/stats/weekly")
def get_weekly_stats():
    repository = current_app.extensions["session_repository"]
    now = datetime.now(timezone.utc)
    today = now.date()
    week_start_date = today - timedelta(days=6)
    week_start = datetime(week_start_date.year, week_start_date.month, week_start_date.day, tzinfo=timezone.utc)

    sessions = repository.list_range(week_start, now + timedelta(days=1))
    days = build_daily_stats(list(sessions), week_start_date, 7)

    return jsonify({"days": days})


@main_blueprint.get("/api/stats/monthly")
def get_monthly_stats():
    repository = current_app.extensions["session_repository"]
    now = datetime.now(timezone.utc)
    today = now.date()
    month_start_date = today - timedelta(days=29)
    month_start = datetime(month_start_date.year, month_start_date.month, month_start_date.day, tzinfo=timezone.utc)

    sessions = repository.list_range(month_start, now + timedelta(days=1))
    days = build_daily_stats(list(sessions), month_start_date, 30)

    return jsonify({"days": days})