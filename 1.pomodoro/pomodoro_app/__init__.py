from pathlib import Path

from flask import Flask

from .repositories import SessionRepository
from .routes import main_blueprint
from .services import TimerConfig
from .time_provider import TimeProvider


def create_app(config: dict | None = None) -> Flask:
    app = Flask(__name__)

    instance_path = Path(app.root_path).parent / "instance"
    instance_path.mkdir(exist_ok=True)

    app.config.update(
        DATABASE_PATH=str(instance_path / "pomodoro.sqlite3"),
        TIMER_CONFIG=TimerConfig(),
    )

    if config:
        app.config.update(config)

    time_provider = TimeProvider()
    session_repository = SessionRepository(
        db_path=app.config["DATABASE_PATH"],
        time_provider=time_provider,
    )

    app.extensions["time_provider"] = time_provider
    app.extensions["session_repository"] = session_repository

    app.register_blueprint(main_blueprint)
    return app