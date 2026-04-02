from datetime import datetime

from flask import Blueprint, current_app, jsonify, render_template, request

from .models import SessionRecord
from .services import TimerConfig, summarize_today


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