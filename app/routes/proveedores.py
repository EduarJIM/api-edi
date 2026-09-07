from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Proveedor
from app.schemas.schemas import proveedor_schema, proveedores_schema

proveedores_bp = Blueprint("proveedores", __name__)


@proveedores_bp.route("/proveedores", methods=["GET"])
def listar_proveedores():
    nombre = request.args.get("nombre", "").strip()
    activo = request.args.get("activo")

    query = Proveedor.query
    if nombre:
        query = query.filter(Proveedor.nombre.ilike(f"%{nombre}%"))
    if activo in ("true", "false"):
        query = query.filter(Proveedor.activo == (activo == "true"))

    proveedores = query.order_by(Proveedor.nombre.asc()).all()
    return jsonify(proveedores_schema.dump(proveedores)), 200


@proveedores_bp.route("/proveedores/<int:proveedor_id>", methods=["GET"])
def obtener_proveedor(proveedor_id):
    proveedor = db.get_or_404(
        Proveedor, proveedor_id, description="Proveedor no encontrado."
    )
    return jsonify(proveedor_schema.dump(proveedor)), 200


@proveedores_bp.route("/proveedores", methods=["POST"])
def crear_proveedor():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    errores = proveedor_schema.validate(data)
    if errores:
        return jsonify({"error": errores}), 400

    if Proveedor.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Ya existe un proveedor con ese email."}), 409

    proveedor = Proveedor(**data)
    db.session.add(proveedor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al guardar el proveedor."}), 409

    return jsonify(proveedor_schema.dump(proveedor)), 201


@proveedores_bp.route("/proveedores/<int:proveedor_id>", methods=["PUT"])
def actualizar_proveedor(proveedor_id):
    proveedor = db.get_or_404(
        Proveedor, proveedor_id, description="Proveedor no encontrado."
    )
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    errores = proveedor_schema.validate(data, partial=True)
    if errores:
        return jsonify({"error": errores}), 400

    if "email" in data:
        existente = Proveedor.query.filter(
            Proveedor.email == data["email"], Proveedor.id != proveedor_id
        ).first()
        if existente:
            return jsonify({"error": "Ya existe un proveedor con ese email."}), 409

    for campo, valor in data.items():
        setattr(proveedor, campo, valor)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al actualizar el proveedor."}), 409

    return jsonify(proveedor_schema.dump(proveedor)), 200


@proveedores_bp.route("/proveedores/<int:proveedor_id>", methods=["DELETE"])
def eliminar_proveedor(proveedor_id):
    proveedor = db.get_or_404(
        Proveedor, proveedor_id, description="Proveedor no encontrado."
    )
    db.session.delete(proveedor)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {
                "error": (
                    "No se puede eliminar el proveedor porque tiene productos "
                    "o pedidos asociados. Inactívalo en su lugar."
                )
            }
        ), 409

    return jsonify({"message": "Proveedor eliminado correctamente."}), 200