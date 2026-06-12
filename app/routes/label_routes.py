"""
label_routes.py

프레임 라벨링 API.

제공 API:
- POST   /api/frames/<frame_id>/labels
- PATCH  /api/labels/<label_id>
- DELETE /api/labels/<label_id>
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.common.responses import success_response, error_response
from app.schemas.label_schema import CreateLabelSchema, UpdateLabelSchema
from app.services.label_service import LabelService

label_bp = Blueprint("label", __name__, url_prefix="/api")


@label_bp.post("/frames/<int:frame_id>/labels")
@jwt_required()
def create_label(frame_id: int):
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = CreateLabelSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="라벨 생성 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        label = LabelService.create_label(
            frame_id=frame_id,
            label_name=data["label_name"],
            confidence=data.get("confidence"),
            source=data.get("source", "manual"),
            is_verified=data.get("is_verified", True)
        )

        return success_response(
            data=label,
            message="라벨 생성 성공",
            status_code=201
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception as e:
        return error_response(
            message="라벨 생성 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@label_bp.patch("/labels/<int:label_id>")
@jwt_required()
def update_label(label_id: int):
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = UpdateLabelSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="라벨 수정 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        label = LabelService.update_label(
            label_id=label_id,
            label_name=data.get("label_name"),
            confidence=data.get("confidence"),
            source=data.get("source"),
            is_verified=data.get("is_verified")
        )

        return success_response(
            data=label,
            message="라벨 수정 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="라벨 수정 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@label_bp.delete("/labels/<int:label_id>")
@jwt_required()
def delete_label(label_id: int):
    try:
        LabelService.delete_label(label_id)

        return success_response(
            data=None,
            message="라벨 삭제 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="라벨 삭제 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )