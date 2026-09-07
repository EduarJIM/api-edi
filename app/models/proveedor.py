from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class Proveedor(db.Model):
    __tablename__ = "proveedores"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    contacto = db.Column(db.String(120), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefono = db.Column(db.String(40), nullable=True)
    direccion = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True, nullable=False)
    creado_en = db.Column(db.DateTime, default=_utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    productos = db.relationship(
        "Producto", back_populates="proveedor", cascade="all, delete-orphan"
    )
    pedidos = db.relationship(
        "Pedido", back_populates="proveedor", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "contacto": self.contacto,
            "email": self.email,
            "telefono": self.telefono,
            "direccion": self.direccion,
            "activo": self.activo,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": (
                self.actualizado_en.isoformat() if self.actualizado_en else None
            ),
        }
