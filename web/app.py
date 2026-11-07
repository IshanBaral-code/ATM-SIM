"""
Flask application factory and configuration for Apex Federal Bank Web Portal.
"""

from datetime import datetime
from pathlib import Path
from flask import Flask

from config import (
    BANK_NAME,
    BANK_TAGLINE,
    CURRENCY_CODE,
    CURRENCY_SYMBOL,
    SUPPORT_PHONE,
    TERMINAL_ID,
    TERMINAL_LOCATION,
)
from storage.database import init_db
from web.routes.admin import admin_bp
from web.routes.api import api_bp
from web.routes.auth import auth_bp
from web.routes.cards import cards_bp
from web.routes.dashboard import dashboard_bp
from web.routes.public import public_bp
from web.routes.transfers import transfers_bp


def create_app() -> Flask:
    """Builds and configures the Flask web application."""
    init_db()  # Ensure tables & initial seed exist

    template_dir = Path(__file__).resolve().parent / "templates"
    static_dir = Path(__file__).resolve().parent / "static"

    app = Flask(
        __name__,
        template_folder=str(template_dir),
        static_folder=str(static_dir)
    )

    app.config["SECRET_KEY"] = "apex-banking-secret-key-2026-university-secure"
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # Context processors for global templates
    @app.context_processor
    def inject_global_vars():
        return {
            "BANK_NAME": BANK_NAME,
            "BANK_TAGLINE": BANK_TAGLINE,
            "TERMINAL_ID": TERMINAL_ID,
            "TERMINAL_LOCATION": TERMINAL_LOCATION,
            "CURRENCY_SYMBOL": CURRENCY_SYMBOL,
            "CURRENCY_CODE": CURRENCY_CODE,
            "SUPPORT_PHONE": SUPPORT_PHONE,
            "current_year": datetime.now().year,
        }

    # Template filters
    @app.template_filter("currency")
    def format_currency(value):
        try:
            return f"{CURRENCY_SYMBOL}{float(value):,.2f}"
        except (ValueError, TypeError):
            return f"{CURRENCY_SYMBOL}0.00"

    # Register blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transfers_bp)
    app.register_blueprint(cards_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    return app
