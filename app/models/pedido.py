from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class Pedido(db.Model):
    __tablename__ = "pedidos"

    id = db.Column(db.Integer, primary_key=True)
    numero_edi = db.Column(db.String(20), unique=True, nullable=False)
    estado = db.Column(
        db.String(20), default="pendiente", nullable=False
    )
    observaciones = db.Column(db.String(500), nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey("proveedores.id"), nullable=False)
    creado_en = db.Column(db.DateTime, default=_utcnow, nullable=False)
    actualizado_en = db.Column(
        db.DateTime, default=_utcnow, onupdate=_utcnow, nullable=False
    )

    proveedor = db.relationship("Proveedor", back_populates="pedidos")
    detalles = db.relationship(
        "DetallePedido",
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    ESTADOS_VALIDOS = ("pendiente", "enviado", "recibido", "cancelado")

    def to_dict(self, incluir_detalles=False):
        data = {
            "id": self.id,
            "numero_edi": self.numero_edi,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "proveedor_id": self.proveedor_id,
            "proveedor_nombre": self.proveedor.nombre if self.proveedor else None,
            "total": self.calcular_total(),
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": (
                self.actualizado_en.isoformat() if self.actualizado_en else None
            ),
        }
        if incluir_detalles:
            data["detalles"] = [
                detalle.to_dict() for detalle in self.detalles
            ]
        return data

    def calcular_total(self):
        total = 0
        for detalle in self.detalles:
            try:
                total += float(detalle.cantidad) * float(detalle.precio_unitario)
            except (TypeError, ValueError):
                continue
        return round(total, 2)
