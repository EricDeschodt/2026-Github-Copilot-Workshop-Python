from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TimerConfig:
    focus_seconds: int = 25 * 60
    short_break_seconds: int = 5 * 60
    long_break_seconds: int = 15 * 60
    sessions_before_long_break: int = 4