from marshmallow import Schema, fields, validate


ALLOWED_LABELS = [
    "fire",
    "smoke",
    "carlight",
    "negative",
    "fire_smoke",
    "fire_smoke_carlight",
]

ALLOWED_SOURCES = [
    "manual",
    "ai",
    "mock",
    "auto",
]


class CreateBoundingBoxSchema(Schema):
    frame_id = fields.Integer(
        required=True,
        error_messages={"required": "프레임 ID는 필수입니다."},
    )

    label_id = fields.Integer(
        required=False,
        allow_none=True,
    )

    label_name = fields.String(
        required=True,
        validate=validate.OneOf(ALLOWED_LABELS),
        error_messages={"required": "라벨명은 필수입니다."},
    )

    x = fields.Float(required=True)
    y = fields.Float(required=True)
    width = fields.Float(required=True)
    height = fields.Float(required=True)

    source = fields.String(
        required=False,
        load_default="manual",
        validate=validate.OneOf(ALLOWED_SOURCES),
    )

    confidence = fields.Float(
        required=False,
        allow_none=True,
    )

    is_verified = fields.Boolean(
        required=False,
        allow_none=True,
    )


class UpdateBoundingBoxSchema(Schema):
    label_name = fields.String(
        required=False,
        validate=validate.OneOf(ALLOWED_LABELS),
    )

    x = fields.Float(required=False)
    y = fields.Float(required=False)
    width = fields.Float(required=False)
    height = fields.Float(required=False)

    source = fields.String(
        required=False,
        validate=validate.OneOf(ALLOWED_SOURCES),
    )

    confidence = fields.Float(
        required=False,
        allow_none=True,
    )

    is_verified = fields.Boolean(required=False)