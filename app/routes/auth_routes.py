from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.common.responses import success_response, error_response
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = RegisterSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="회원가입 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        user = AuthService.register(
            name=data["name"],
            birth_date=data["birth_date"],
            nickname=data["nickname"],
            email=data["email"],
            password=data["password"]
        )

        return success_response(
            data=user,
            message="회원가입 성공",
            status_code=201
        )

    except ValueError as e:
        return error_response(str(e), 409)

    except Exception as e:
        return error_response(
            message="회원가입 처리 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@auth_bp.post("/login")
def login():
    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    try:
        data = LoginSchema().load(json_data)
    except ValidationError as err:
        return error_response(
            message="로그인 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        result = AuthService.login(
            email=data["email"],
            password=data["password"]
        )

        return success_response(
            data=result,
            message="로그인 성공"
        )

    except ValueError as e:
        return error_response(str(e), 401)

    except Exception as e:
        return error_response(
            message="로그인 처리 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())

    user = AuthService.get_user_by_id(user_id)

    if not user:
        return error_response("사용자를 찾을 수 없습니다.", 404)

    return success_response(
        data=AuthService.serialize_user(user),
        message="현재 사용자 조회 성공"
    )