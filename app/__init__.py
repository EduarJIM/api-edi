import decimal
import os
import click
from flask import Flask, jsonify, render_template, request
from flask.json.provider import DefaultJSONProvider
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()


class NumericJSONProvider(DefaultJSONProvider):
    @staticmethod
    def default(o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return DefaultJSONProvider.default(o)


def create_app(config_name=None):
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "development")

    from app.config import config_by_name

    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(config_by_name[config_name])
    app.json = NumericJSONProvider(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.tareas import tareas_bp

    app.register_blueprint(tareas_bp, url_prefix="/api")

    @app.route("/")
    def index():
        if (
            request.headers.get("Accept") == "application/json"
            or request.args.get("format") == "json"
        ):
            return api_info()
        return render_template("index.html")

    @app.route("/api")
    @app.route("/api/")
    def api_info():
        return (
            jsonify(
                {
                    "service": "api-edi",
                    "version": "1.0.0",
                    "estado": "ok",
                    "documentacion": "Ver README.md del proyecto",
                    "endpoints": {
                        "health": "/api/health",
                        "tareas": "/api/tareas",
                    },
                }
            ),
            200,
        )

    @app.route("/health", methods=["GET", "POST"])
    @app.route("/api/health", methods=["GET", "POST"])
    def health_check():
        return jsonify({"status": "healthy", "service": "api-edi"}), 200

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        click.echo("Base de datos inicializada: tablas creadas.")

    return app
