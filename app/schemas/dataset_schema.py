"""
dataset_schema.py

데이터셋 프로젝트 관련 요청 데이터 검증 스키마.

제공 Schema:
- CreateDatasetSchema
- UpdateDatasetSchema

초기 MVP에서는 생성 기능만 먼저 사용한다.
"""

from marshmallow import Schema, fields, validate


class CreateDatasetSchema(Schema):
    """
    데이터셋 프로젝트 생성 요청 검증용 Schema.

    요청 예:
    {
        "name": "도로 화재 데이터셋",
        "description": "도로 및 터널 환경의 화재/연기 이미지 데이터셋"
    }
    """

    name = fields.String(
        required=True,
        validate=validate.Length(min=2, max=200),
        error_messages={
            "required": "데이터셋 이름은 필수입니다."
        }
    )

    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )


class UpdateDatasetSchema(Schema):
    """
    데이터셋 프로젝트 수정 요청 검증용 Schema.

    아직 라우트는 만들지 않지만,
    나중에 PATCH /api/datasets/<id> 구현 시 사용한다.
    """

    name = fields.String(
        required=False,
        validate=validate.Length(min=2, max=200)
    )

    description = fields.String(
        required=False,
        allow_none=True,
        validate=validate.Length(max=1000)
    )