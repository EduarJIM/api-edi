from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
import uuid

from app import db
from app.models import Tarea

tareas_bp = Blueprint("tareas", __name__)


def generate_task_code():
    count = Tarea.query.count() + 1
    return f"TSK-{count:03d}"


@tareas_bp.route("/tareas", methods=["GET"])
@tareas_bp.route("/tasks", methods=["GET"])
def listar_tareas():
    q = request.args.get("q", "").strip()
    codigo = request.args.get("codigo", "").strip()
    estado = request.args.get("estado", "").strip()
    prioridad = request.args.get("prioridad", "").strip()
    completed_param = request.args.get("completed")

    query = Tarea.query
    if q:
        search_filter = f"%{q}%"
        query = query.filter(
            (Tarea.codigo.ilike(search_filter))
            | (Tarea.titulo.ilike(search_filter))
            | (Tarea.descripcion.ilike(search_filter))
        )
    if codigo:
        query = query.filter(Tarea.codigo.ilike(f"%{codigo}%"))
    if estado:
        query = query.filter(Tarea.estado == estado)
    if prioridad:
        query = query.filter(Tarea.prioridad == prioridad)

    if completed_param is not None:
        is_comp = completed_param.lower() in ("true", "1")
        if is_comp:
            query = query.filter(Tarea.estado == "completado")
        else:
            query = query.filter(Tarea.estado != "completado")

    tareas = query.order_by(Tarea.creado_en.desc()).all()
    return jsonify([t.to_dict() for t in tareas]), 200


@tareas_bp.route("/tareas/<int:tarea_id>", methods=["GET"])
@tareas_bp.route("/tasks/<int:tarea_id>", methods=["GET"])
def obtener_tarea(tarea_id):
    tarea = db.get_or_404(Tarea, tarea_id, description="Tarea no encontrada.")
    return jsonify(tarea.to_dict()), 200


@tareas_bp.route("/tareas", methods=["POST"])
@tareas_bp.route("/tasks", methods=["POST"])
def crear_tarea():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    # Field Mappings for evidence guide (title -> titulo, description -> descripcion, completed -> estado)
    titulo = data.get("title") or data.get("titulo")
    if not titulo:
        return jsonify({"error": "El título de la tarea ('title' o 'titulo') es obligatorio."}), 400

    descripcion = data.get("description") if "description" in data else data.get("descripcion", "")
    
    if "completed" in data:
        estado = "completado" if data["completed"] else "pendiente"
    else:
        estado = data.get("estado", "pendiente")

    prioridad = data.get("prioridad", "media")

    codigo = data.get("codigo")
    if not codigo:
        codigo = generate_task_code()
        # Ensure uniqueness
        while Tarea.query.filter_by(codigo=codigo).first():
            codigo = f"TSK-{uuid.uuid4().hex[:4].upper()}"

    if Tarea.query.filter_by(codigo=codigo).first():
        return jsonify({"error": f"Ya existe una tarea con el código '{codigo}'."}), 409

    tarea = Tarea(
        codigo=codigo,
        titulo=titulo,
        descripcion=descripcion,
        estado=estado,
        prioridad=prioridad
    )
    db.session.add(tarea)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al guardar la tarea."}), 409

    return jsonify(tarea.to_dict()), 201


@tareas_bp.route("/tareas/<int:tarea_id>", methods=["PUT", "PATCH"])
@tareas_bp.route("/tasks/<int:tarea_id>", methods=["PUT", "PATCH"])
def actualizar_tarea(tarea_id):
    tarea = db.get_or_404(Tarea, tarea_id, description="Tarea no encontrada.")
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    if "title" in data:
        tarea.titulo = data["title"]
    elif "titulo" in data:
        tarea.titulo = data["titulo"]

    if "description" in data:
        tarea.descripcion = data["description"]
    elif "descripcion" in data:
        tarea.descripcion = data["descripcion"]

    if "completed" in data:
        tarea.estado = "completado" if data["completed"] else "pendiente"
    elif "estado" in data:
        tarea.estado = data["estado"]

    if "prioridad" in data:
        tarea.prioridad = data["prioridad"]

    if "codigo" in data and data["codigo"] != tarea.codigo:
        existente = Tarea.query.filter(
            Tarea.codigo == data["codigo"], Tarea.id != tarea_id
        ).first()
        if existente:
            return jsonify({"error": f"Ya existe otra tarea con el código '{data['codigo']}'."}), 409
        tarea.codigo = data["codigo"]

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al actualizar la tarea."}), 409

    return jsonify(tarea.to_dict()), 200


@tareas_bp.route("/tareas/<int:tarea_id>/suspender", methods=["PUT"])
@tareas_bp.route("/tasks/<int:tarea_id>/suspender", methods=["PUT"])
def suspender_tarea(tarea_id):
    tarea = db.get_or_404(Tarea, tarea_id, description="Tarea no encontrada.")
    if tarea.estado == "suspendido":
        tarea.estado = "pendiente"
        mensaje = "Tarea reanudada correctamente."
    else:
        tarea.estado = "suspendido"
        mensaje = "Tarea suspendida correctamente."

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Error al cambiar estado."}), 409

    return jsonify({"mensaje": mensaje, "tarea": tarea.to_dict()}), 200


@tareas_bp.route("/tareas/<int:tarea_id>", methods=["DELETE"])
@tareas_bp.route("/tasks/<int:tarea_id>", methods=["DELETE"])
def eliminar_tarea(tarea_id):
    tarea = db.get_or_404(Tarea, tarea_id, description="Tarea no encontrada.")
    db.session.delete(tarea)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al eliminar la tarea."}), 409

    return jsonify({"message": "Tarea eliminada correctamente.", "id": tarea_id}), 200
