from datetime import timezone

from pomodoro_app.time_provider import TimeProvider


def test_time_provider_returns_timezone_aware_utc_datetime() -> None:
    now = TimeProvider().now()

    assert now.tzinfo is not None
    assert now.utcoffset() == timezone.utc.utcoffset(now)