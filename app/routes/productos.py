from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import Producto, Proveedor
from app.schemas.schemas import producto_schema, productos_schema

productos_bp = Blueprint("productos", __name__)


@productos_bp.route("/productos", methods=["GET"])
def listar_productos():
    categoria = request.args.get("categoria", "").strip()
    proveedor_id = request.args.get("proveedor_id")
    nombre = request.args.get("nombre", "").strip()
    stock_minimo = request.args.get("stock_minimo", type=int)

    query = Producto.query
    if categoria:
        query = query.filter(Producto.categoria.ilike(f"%{categoria}%"))
    if nombre:
        query = query.filter(Producto.nombre.ilike(f"%{nombre}%"))
    if proveedor_id:
        query = query.filter(Producto.proveedor_id == proveedor_id)
    if stock_minimo is not None:
        query = query.filter(Producto.stock >= stock_minimo)

    productos = query.order_by(Producto.nombre.asc()).all()
    return jsonify(productos_schema.dump(productos)), 200


@productos_bp.route("/productos/<int:producto_id>", methods=["GET"])
def obtener_producto(producto_id):
    producto = db.get_or_404(
        Producto, producto_id, description="Producto no encontrado."
    )
    return jsonify(producto_schema.dump(producto)), 200


@productos_bp.route("/productos", methods=["POST"])
def crear_producto():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    errores = producto_schema.validate(data)
    if errores:
        return jsonify({"error": errores}), 400

    if not db.session.get(Proveedor, data["proveedor_id"]):
        return jsonify({"error": "El proveedor indicado no existe."}), 400

    producto = Producto(**data)
    db.session.add(producto)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al guardar el producto."}), 409

    return jsonify(producto_schema.dump(producto)), 201


@productos_bp.route("/productos/<int:producto_id>", methods=["PUT"])
def actualizar_producto(producto_id):
    producto = db.get_or_404(
        Producto, producto_id, description="Producto no encontrado."
    )
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la petición no es JSON válido."}), 400

    errores = producto_schema.validate(data, partial=True)
    if errores:
        return jsonify({"error": errores}), 400

    if "proveedor_id" in data and not db.session.get(Proveedor, data["proveedor_id"]):
        return jsonify({"error": "El proveedor indicado no existe."}), 400

    for campo, valor in data.items():
        setattr(producto, campo, valor)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al actualizar el producto."}), 409

    return jsonify(producto_schema.dump(producto)), 200


@productos_bp.route("/productos/<int:producto_id>", methods=["DELETE"])
def eliminar_producto(producto_id):
    producto = db.get_or_404(
        Producto, producto_id, description="Producto no encontrado."
    )
    db.session.delete(producto)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(
            {
                "error": (
                    "No se puede eliminar el producto porque está asociado "
                    "a uno o más pedidos."
                )
            }
        ), 409

    return jsonify({"message": "Producto eliminado correctamente."}), 200