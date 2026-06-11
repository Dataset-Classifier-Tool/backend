"""
auth_routes.py

인증 관련 API 라우트.

제공 API:
- POST /api/auth/register
- POST /api/auth/login
- GET  /api/auth/me
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.common.responses import success_response, error_response
from app.schemas.auth_schema import RegisterSchema, LoginSchema
from app.services.auth_service import AuthService

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    """
    회원가입 API.

    요청 예:
    {
        "email": "test@test.com",
        "password": "12345678",
        "nickname": "도균"
    }
    """

    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    schema = RegisterSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return error_response(
            message="회원가입 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        user = AuthService.register(
            email=data["email"],
            password=data["password"],
            nickname=data["nickname"]
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
    """
    로그인 API.

    요청 예:
    {
        "email": "test@test.com",
        "password": "12345678"
    }
    """

    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    schema = LoginSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return error_response(
            message="로그인 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        login_result = AuthService.login(
            email=data["email"],
            password=data["password"]
        )

        return success_response(
            data=login_result,
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
    """
    현재 로그인 사용자 정보 조회 API.

    요청 Header:
    Authorization: Bearer access_token
    """

    user_id = get_jwt_identity()

    user = AuthService.get_user_by_id(int(user_id))

    if not user:
        return error_response("사용자를 찾을 수 없습니다.", 404)

    return success_response(
        data=AuthService.serialize_user(user),
        message="현재 사용자 조회 성공"
    )