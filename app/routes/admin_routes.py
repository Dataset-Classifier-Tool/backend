from flask import Blueprint, request
from marshmallow import ValidationError

from app.common.decorators import admin_required
from app.common.responses import success_response, error_response
from app.schemas.admin_schema import UpdateMembershipSchema, UpdateActiveSchema
from app.services.admin_service import AdminService

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@admin_bp.get("/users")
@admin_required
def get_users():
    users = AdminService.get_all_users()

    return success_response(
        data=users,
        message="회원 목록 조회 성공"
    )


@admin_bp.patch("/users/<int:user_id>/membership")
@admin_required
def update_user_membership(user_id: int):
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = UpdateMembershipSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="회원 등급 변경 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        user = AdminService.update_membership(
            user_id=user_id,
            membership_type=data["membership_type"]
        )

        return success_response(
            data=user,
            message="회원 등급 변경 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)


@admin_bp.patch("/users/<int:user_id>/active")
@admin_required
def update_user_active(user_id: int):
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = UpdateActiveSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="회원 활성화 상태 변경 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        user = AdminService.update_active(
            user_id=user_id,
            is_active=data["is_active"]
        )

        return success_response(
            data=user,
            message="회원 활성화 상태 변경 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)