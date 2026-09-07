import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.db"
    os.environ["TEST_DATABASE_URL"] = f"sqlite:///{db_path}"

    from app import create_app

    test_app = create_app("testing")
    test_app.config["TESTING"] = True

    from app import db as _db

    with test_app.app_context():
        _db.create_all()

    yield test_app

    with test_app.app_context():
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def proveedor_payload():
    return {
        "nombre": "Proveedor Test",
        "contacto": "Juan Pérez",
        "email": "juan@proveedor.com",
        "telefono": "+34600111222",
        "direccion": "Calle Falsa 123",
        "activo": True,
    }