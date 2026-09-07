from marshmallow import Schema, fields, validate, ValidationError, pre_load


def validar_email(valor):
    if "@" not in valor or "." not in valor.split("@")[-1]:
        raise ValidationError("Email con formato inválido.")
    return valor


class ProveedorSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=2, max=120))
    contacto = fields.Str(allow_none=True, validate=validate.Length(max=120))
    email = fields.Str(required=True, validate=validar_email)
    telefono = fields.Str(allow_none=True, validate=validate.Length(max=40))
    direccion = fields.Str(allow_none=True, validate=validate.Length(max=255))
    activo = fields.Bool(load_default=True)
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)


class ProductoSchema(Schema):
    id = fields.Int(dump_only=True)
    nombre = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    descripcion = fields.Str(allow_none=True, validate=validate.Length(max=500))
    precio = fields.Decimal(required=True, places=2, as_string=False)
    stock = fields.Int(load_default=0, validate=validate.Range(min=0))
    categoria = fields.Str(allow_none=True, validate=validate.Length(max=80))
    proveedor_id = fields.Int(required=True)
    proveedor_nombre = fields.Str(dump_only=True)
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)

    @pre_load
    def validar_precio(self, data, **kwargs):
        if "precio" in data and data["precio"] is not None:
            try:
                valor = float(data["precio"])
            except (TypeError, ValueError):
                raise ValidationError({"precio": ["Debe ser un número válido."]})
            if valor < 0:
                raise ValidationError({"precio": ["No puede ser negativo."]})
            if valor > 9999999999.99:
                raise ValidationError({"precio": ["Valor demasiado grande."]})
            data["precio"] = round(valor, 2)
        return data


class DetallePedidoSchema(Schema):
    id = fields.Int(dump_only=True)
    pedido_id = fields.Int(dump_only=True)
    producto_id = fields.Int(required=True)
    producto_nombre = fields.Str(dump_only=True)
    cantidad = fields.Int(required=True, validate=validate.Range(min=1))
    precio_unitario = fields.Decimal(required=True, places=2, as_string=False)
    subtotal = fields.Decimal(dump_only=True)
    creado_en = fields.DateTime(dump_only=True)


class PedidoSchema(Schema):
    id = fields.Int(dump_only=True)
    numero_edi = fields.Str(required=True, validate=validate.Length(min=3, max=20))
    estado = fields.Str(
        load_default="pendiente",
        validate=validate.OneOf(["pendiente", "enviado", "recibido", "cancelado"]),
    )
    observaciones = fields.Str(allow_none=True, validate=validate.Length(max=500))
    proveedor_id = fields.Int(required=True)
    proveedor_nombre = fields.Str(dump_only=True)
    total = fields.Decimal(dump_only=True)
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)
    detalles = fields.List(
        fields.Nested(DetallePedidoSchema()),
        required=True,
        validate=validate.Length(min=1),
    )


proveedor_schema = ProveedorSchema()
proveedores_schema = ProveedorSchema(many=True)
producto_schema = ProductoSchema()
productos_schema = ProductoSchema(many=True)
pedido_schema = PedidoSchema()
pedidos_schema = PedidoSchema(many=True)
detalle_schema = DetallePedidoSchema()