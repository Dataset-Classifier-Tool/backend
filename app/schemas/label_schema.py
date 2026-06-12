"""
label_schema.py

프레임 라벨링 요청 검증 스키마.
"""

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
]


class CreateLabelSchema(Schema):
    label_name = fields.String(
        required=True,
        validate=validate.OneOf(ALLOWED_LABELS),
        error_messages={"required": "라벨명은 필수입니다."}
    )

    confidence = fields.Float(
        required=False,
        allow_none=True
    )

    source = fields.String(
        required=False,
        load_default="manual",
        validate=validate.OneOf(ALLOWED_SOURCES)
    )

    is_verified = fields.Boolean(
        required=False,
        load_default=True
    )


class UpdateLabelSchema(Schema):
    label_name = fields.String(
        required=False,
        validate=validate.OneOf(ALLOWED_LABELS)
    )

    confidence = fields.Float(
        required=False,
        allow_none=True
    )

    source = fields.String(
        required=False,
        validate=validate.OneOf(ALLOWED_SOURCES)
    )

    is_verified = fields.Boolean(
        required=False
    )