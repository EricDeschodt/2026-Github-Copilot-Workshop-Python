from datetime import datetime, timezone

import pytest

from pomodoro_app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(
        {
            "TESTING": True,
            "DATABASE_PATH": str(tmp_path / "integration.sqlite3"),
        }
    )

    with app.test_client() as test_client:
        yield test_client


def test_index_renders_main_template(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert b"Pomodoro Timer" in response.data
    assert b"Today's progress" in response.data


def test_get_config_returns_timer_settings(client) -> None:
    response = client.get("/api/config")

    assert response.status_code == 200
    assert response.get_json() == {
        "focus_seconds": 1500,
        "short_break_seconds": 300,
        "long_break_seconds": 900,
        "sessions_before_long_break": 4,
    }


def test_get_today_stats_returns_zeroed_summary_initially(client) -> None:
    response = client.get("/api/stats/today")

    assert response.status_code == 200
    assert response.get_json() == {
        "sessions_completed": 0,
        "focus_minutes": 0,
        "current_streak": 0,
    }


def test_post_session_persists_focus_session_and_updates_stats(client) -> None:
    response = client.post(
        "/api/sessions",
        json={
            "session_type": "focus",
            "duration_seconds": 1500,
            "started_at": datetime(2026, 4, 2, 9, 0, tzinfo=timezone.utc).isoformat(),
            "completed_at": datetime(2026, 4, 2, 9, 25, tzinfo=timezone.utc).isoformat(),
        },
    )

    assert response.status_code == 201

    stats_response = client.get("/api/stats/today")

    assert stats_response.get_json() == {
        "sessions_completed": 1,
        "focus_minutes": 25,
        "current_streak": 1,
    }


def test_post_session_rejects_invalid_payload(client) -> None:
    response = client.post(
        "/api/sessions",
        json={
            "session_type": "invalid",
            "duration_seconds": "bad-value",
        },
    )

    assert response.status_code == 400