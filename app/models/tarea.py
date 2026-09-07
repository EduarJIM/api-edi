from datetime import datetime
from app import db


class Tarea(db.Model):
    __tablename__ = "tareas"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False, index=True)
    titulo = db.Column(db.String(150), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    estado = db.Column(db.String(30), default="pendiente", nullable=False)
    prioridad = db.Column(db.String(30), default="media", nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self):
        is_completed = self.estado == "completado"
        return {
            "id": self.id,
            "codigo": self.codigo,
            "title": self.titulo,
            "titulo": self.titulo,
            "description": self.descripcion or "",
            "descripcion": self.descripcion or "",
            "completed": is_completed,
            "estado": self.estado,
            "prioridad": self.prioridad,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": (
                self.actualizado_en.isoformat() if self.actualizado_en else None
            ),
        }
