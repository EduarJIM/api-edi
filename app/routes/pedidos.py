from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app import db
from app.models import DetallePedido, Pedido, Producto, Proveedor
from app.schemas.schemas import pedido_schema, pedidos_schema

pedidos_bp = Blueprint("pedidos", __name__)


@pedidos_bp.route("/pedidos", methods=["GET"])
def listar_pedidos():
    proveedor_id = request.args.get("proveedor_id")
    estado = request.args.get("estado", "").strip()
    numero_edi = request.args.get("numero_edi", "").strip()

    query = Pedido.query
    if proveedor_id:
        query = query.filter(Pedido.proveedor_id == proveedor_id)
    if estado:
        query = query.filter(Pedido.estado == estado)
    if numero_edi:
        query = query.filter(Pedido.numero_edi == numero_edi)

    pedidos = query.order_by(Pedido.creado_en.desc()).all()
    return jsonify(pedidos_schema.dump(pedidos)), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>", methods=["GET"])
def obtener_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id, description="Pedido no encontrado.")
    return jsonify(pedido.to_dict(incluir_detalles=True)), 200


@pedidos_bp.route("/pedidos", methods=["POST"])
def crear_pedido():
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la peticiÃ³n no es JSON vÃ¡lido."}), 400

    errores = pedido_schema.validate(data)
    if errores:
        return jsonify({"error": errores}), 400

    if not db.session.get(Proveedor, data["proveedor_id"]):
        return jsonify({"error": "El proveedor indicado no existe."}), 400

    if Pedido.query.filter_by(numero_edi=data["numero_edi"]).first():
        return jsonify({"error": "Ya existe un pedido con ese nÃºmero EDI."}), 409

    detalles_data = data.pop("detalles")
    producto_ids = [d["producto_id"] for d in detalles_data]
    productos = Producto.query.filter(Producto.id.in_(producto_ids)).all()
    producto_map = {p.id: p for p in productos}
    if len(producto_map) != len(set(producto_ids)):
        return jsonify({"error": "Uno o mÃ¡s productos indicados no existen."}), 400

    pedido = Pedido(**data)
    for detalle in detalles_data:
        producto = producto_map[detalle["producto_id"]]
        pedido.detalles.append(
            DetallePedido(
                producto_id=producto.id,
                cantidad=detalle["cantidad"],
                precio_unitario=round(float(detalle["precio_unitario"]), 2),
            )
        )
        if producto.stock is not None:
            producto.stock = max(0, producto.stock - detalle["cantidad"])

    db.session.add(pedido)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al guardar el pedido."}), 409

    resultado = pedido.to_dict(incluir_detalles=True)
    return jsonify(resultado), 201


@pedidos_bp.route("/pedidos/<int:pedido_id>", methods=["PUT"])
def actualizar_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id, description="Pedido no encontrado.")
    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la peticiÃ³n no es JSON vÃ¡lido."}), 400

    errores = pedido_schema.validate(data, partial=True)
    if errores:
        return jsonify({"error": errores}), 400

    if "proveedor_id" in data and not db.session.get(Proveedor, data["proveedor_id"]):
        return jsonify({"error": "El proveedor indicado no existe."}), 400

    if "numero_edi" in data:
        existente = Pedido.query.filter(
            Pedido.numero_edi == data["numero_edi"], Pedido.id != pedido_id
        ).first()
        if existente:
            return jsonify({"error": "Ya existe un pedido con ese nÃºmero EDI."}), 409

    if "detalles" in data:
        return jsonify(
            {
                "error": (
                    "Los detalles de un pedido no se pueden reemplazar. "
                    "Elimina el pedido y crÃ©alo de nuevo, o usa "
                    "POST /api/pedidos/<id>/detalles para aÃ±adir lÃ­neas."
                )
            }
        ), 400

    for campo, valor in data.items():
        setattr(pedido, campo, valor)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al actualizar el pedido."}), 409

    return jsonify(pedido.to_dict(incluir_detalles=True)), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>", methods=["DELETE"])
def eliminar_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id, description="Pedido no encontrado.")
    db.session.delete(pedido)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al eliminar el pedido."}), 409

    return jsonify({"message": "Pedido eliminado correctamente."}), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>/detalles", methods=["GET"])
def listar_detalles_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id, description="Pedido no encontrado.")
    detalles = DetallePedido.query.filter_by(pedido_id=pedido.id).all()
    return jsonify([d.to_dict() for d in detalles]), 200


@pedidos_bp.route("/pedidos/<int:pedido_id>/detalles", methods=["POST"])
def agregar_detalle_pedido(pedido_id):
    pedido = db.get_or_404(Pedido, pedido_id, description="Pedido no encontrado.")
    if pedido.estado in ("enviado", "cancelado"):
        return jsonify(
            {
                "error": (
                    f"No se pueden modificar los detalles de un pedido "
                    f"en estado '{pedido.estado}'."
                )
            }
        ), 400

    data = request.get_json(silent=True)
    if data is None or not isinstance(data, dict):
        return jsonify({"error": "El cuerpo de la peticiÃ³n no es JSON vÃ¡lido."}), 400

    from app.schemas.schemas import detalle_schema

    errores = detalle_schema.validate(
        {**data, "pedido_id": pedido.id}, partial=True
    )
    if errores:
        return jsonify({"error": errores}), 400

    producto = db.session.get(Producto, data["producto_id"])
    if not producto:
        return jsonify({"error": "El producto indicado no existe."}), 400

    detalle = DetallePedido(
        pedido_id=pedido.id,
        producto_id=producto.id,
        cantidad=data["cantidad"],
        precio_unitario=round(float(data["precio_unitario"]), 2),
    )
    db.session.add(detalle)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Conflicto al guardar el detalle."}), 409

    return jsonify(detalle.to_dict()), 201

