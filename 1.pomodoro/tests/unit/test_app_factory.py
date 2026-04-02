from pomodoro_app import create_app


def test_create_app_registers_root_route() -> None:
    app = create_app()

    routes = {str(rule) for rule in app.url_map.iter_rules()}

    assert "/" in routes


def test_create_app_applies_config_override() -> None:
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret"})

    assert app.config["TESTING"] is True
    assert app.config["SECRET_KEY"] == "test-secret"


def test_create_app_registers_api_routes() -> None:
    app = create_app()

    routes = {str(rule) for rule in app.url_map.iter_rules()}

    assert "/api/config" in routes
    assert "/api/stats/today" in routes
    assert "/api/sessions" in routes
    assert "/api/stats/gamification" in routes
    assert "/api/stats/weekly" in routes
    assert "/api/stats/monthly" in routes