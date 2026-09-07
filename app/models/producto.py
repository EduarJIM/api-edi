from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class Producto(db.Model):
    __tablename__ = "productos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.String(500), nullable=True)
    precio = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    categoria = db.Column(db.String(80), nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    creado_en = db.Column(db.DateTime, default=_utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    proveedor = db.relationship("Proveedor", back_populates="productos")
    detalles = db.relationship(
        "DetallePedido", back_populates="producto", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion,
            "precio": float(self.precio) if self.precio is not None else None,
            "stock": self.stock,
            "categoria": self.categoria,
            "proveedor_id": self.proveedor_id,
            "proveedor_nombre": self.proveedor.nombre if self.proveedor else None,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": (
                self.actualizado_en.isoformat() if self.actualizado_en else None
            ),
        }
