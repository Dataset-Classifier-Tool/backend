from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

from app.common.exceptions import AppError
from app.common.responses import success_response, error_response
from app.schemas.bounding_box_schema import (
    CreateBoundingBoxSchema,
    UpdateBoundingBoxSchema,
)
from app.services.bounding_box_service import BoundingBoxService


bounding_box_bp = Blueprint("bounding_box", __name__, url_prefix="/api")


@bounding_box_bp.post("/bounding-boxes")
@jwt_required()
def create_bounding_box():
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = CreateBoundingBoxSchema().load(json_data)
    except ValidationError as error:
        return error_response(
            message="라벨링 박스 생성 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=error.messages
        )

    try:
        box = BoundingBoxService.create_box(data)

        return success_response(
            data=box,
            message="라벨링 박스 생성 성공",
            status_code=201
        )

    except AppError as error:
        return error_response(error.message, error.status_code, error.details)


@bounding_box_bp.get("/frames/<int:frame_id>/bounding-boxes")
@jwt_required()
def get_frame_bounding_boxes(frame_id: int):
    try:
        boxes = BoundingBoxService.get_frame_boxes(frame_id)

        return success_response(
            data=boxes,
            message="프레임 라벨링 박스 조회 성공"
        )

    except AppError as error:
        return error_response(error.message, error.status_code, error.details)


@bounding_box_bp.patch("/bounding-boxes/<int:box_id>")
@jwt_required()
def update_bounding_box(box_id: int):
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = UpdateBoundingBoxSchema().load(json_data)
    except ValidationError as error:
        return error_response(
            message="라벨링 박스 수정 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=error.messages
        )

    try:
        box = BoundingBoxService.update_box(box_id, data)

        return success_response(
            data=box,
            message="라벨링 박스 수정 성공"
        )

    except AppError as error:
        return error_response(error.message, error.status_code, error.details)


@bounding_box_bp.delete("/bounding-boxes/<int:box_id>")
@jwt_required()
def delete_bounding_box(box_id: int):
    try:
        BoundingBoxService.delete_box(box_id)

        return success_response(
            data=None,
            message="라벨링 박스 삭제 성공"
        )

    except AppError as error:
        return error_response(error.message, error.status_code, error.details)