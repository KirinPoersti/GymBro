from flask import Flask

from .auth import bp as auth_bp
from .dashboard import bp as dashboard_bp
from .training import bp as training_bp
from .meals import bp as meals_bp
from .settings import bp as settings_bp
from .plans_forum import bp as plans_forum_bp


def register_blueprints(app: Flask) -> None:
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(training_bp)
    app.register_blueprint(meals_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(plans_forum_bp)

