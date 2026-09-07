import decimal
import os
import click
from flask import Flask, jsonify
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

    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    app.json = NumericJSONProvider(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app.routes.proveedores import proveedores_bp
    from app.routes.productos import productos_bp
    from app.routes.pedidos import pedidos_bp

    app.register_blueprint(proveedores_bp, url_prefix="/api")
    app.register_blueprint(productos_bp, url_prefix="/api")
    app.register_blueprint(pedidos_bp, url_prefix="/api")

    @app.route("/")
    def index():
        return (
            jsonify(
                {
                    "service": "api-edi",
                    "version": "1.0.0",
                    "estado": "ok",
                    "documentacion": "Ver README.md del proyecto",
                    "endpoints": {
                        "health": "/api/health",
                        "proveedores": "/api/proveedores",
                        "productos": "/api/productos",
                        "pedidos": "/api/pedidos",
                        "detalles_pedido": "/api/pedidos/<id>/detalles",
                    },
                }
            ),
            200,
        )

    @app.route("/api/health")
    def health_check():
        return jsonify({"status": "healthy", "service": "api-edi"}), 200

    @app.cli.command("init-db")
    def init_db_command():
        db.create_all()
        click.echo("Base de datos inicializada: tablas creadas.")

    return app
