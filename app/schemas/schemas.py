from marshmallow import Schema, fields, validate


class TareaSchema(Schema):
    id = fields.Int(dump_only=True)
    codigo = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=50),
        error_messages={"required": "El código de la tarea es obligatorio."},
    )
    titulo = fields.Str(
        required=True,
        validate=validate.Length(min=2, max=150),
        error_messages={"required": "El título de la tarea es obligatorio."},
    )
    descripcion = fields.Str(allow_none=True, load_default="")
    estado = fields.Str(
        load_default="pendiente",
        validate=validate.OneOf(
            ["pendiente", "en_progreso", "completado", "suspendido"],
            error="Estado no válido. Use 'pendiente', 'en_progreso', 'completado' o 'suspendido'.",
        ),
    )
    prioridad = fields.Str(
        load_default="media",
        validate=validate.OneOf(
            ["baja", "media", "alta", "critica"],
            error="Prioridad no válida. Use 'baja', 'media', 'alta' o 'critica'.",
        ),
    )
    creado_en = fields.DateTime(dump_only=True)
    actualizado_en = fields.DateTime(dump_only=True)


tarea_schema = TareaSchema()
tareas_schema = TareaSchema(many=True)