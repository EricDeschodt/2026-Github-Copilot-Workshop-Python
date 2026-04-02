from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class SessionRecord:
    session_type: str
    duration_seconds: int
    started_at: datetime
    completed_at: datetime | None = None


    @property
    def is_completed(self) -> bool:
        return self.completed_at is not None