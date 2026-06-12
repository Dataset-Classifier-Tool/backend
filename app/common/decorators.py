from functools import wraps

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.responses import error_response
from app.services.auth_service import AuthService


def admin_required(fn):
    """
    관리자 전용 API 보호 데코레이터.
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())

        user = AuthService.get_user_by_id(user_id)

        if not user:
            return error_response("사용자를 찾을 수 없습니다.", 404)

        if not user.is_active:
            return error_response("비활성화된 계정입니다.", 403)

        if user.membership_type != "admin":
            return error_response("관리자 권한이 필요합니다.", 403)

        return fn(*args, **kwargs)

    return wrapper