from dataclasses import FrozenInstanceError

import pytest

from pomodoro_app.services.timer_service import TimerConfig


def test_timer_config_uses_expected_defaults() -> None:
    config = TimerConfig()

    assert config.focus_seconds == 25 * 60
    assert config.short_break_seconds == 5 * 60
    assert config.long_break_seconds == 15 * 60
    assert config.sessions_before_long_break == 4


def test_timer_config_accepts_custom_values() -> None:
    config = TimerConfig(
        focus_seconds=30 * 60,
        short_break_seconds=10 * 60,
        long_break_seconds=20 * 60,
        sessions_before_long_break=3,
    )

    assert config.focus_seconds == 30 * 60
    assert config.short_break_seconds == 10 * 60
    assert config.long_break_seconds == 20 * 60
    assert config.sessions_before_long_break == 3


def test_timer_config_is_immutable() -> None:
    config = TimerConfig()

    with pytest.raises(FrozenInstanceError):
        config.focus_seconds = 10