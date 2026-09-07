from datetime import datetime, timezone

from app import db


def _utcnow():
    return datetime.now(timezone.utc)


class DetallePedido(db.Model):
    __tablename__ = "detalle_pedidos"

    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedidos.id"), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey("productos.id"), nullable=False)
    cantidad = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Numeric(12, 2), nullable=False)
    creado_en = db.Column(db.DateTime, default=_utcnow, nullable=False)

    pedido = db.relationship("Pedido", back_populates="detalles")
    producto = db.relationship("Producto", back_populates="detalles")

    def to_dict(self):
        return {
            "id": self.id,
            "pedido_id": self.pedido_id,
            "producto_id": self.producto_id,
            "producto_nombre": self.producto.nombre if self.producto else None,
            "cantidad": self.cantidad,
            "precio_unitario": (
                float(self.precio_unitario)
                if self.precio_unitario is not None
                else None
            ),
            "subtotal": round(
                float(self.cantidad) * float(self.precio_unitario), 2
            )
            if self.cantidad and self.precio_unitario
            else None,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
        }
