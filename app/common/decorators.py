"""
decorators.py

공통 인증/권한 데코레이터 모음.

초기 제공:
- admin_required

나중에 추가 가능:
- premium_required
- active_user_required
- quota_required
"""

from functools import wraps

from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.responses import error_response
from app.services.auth_service import AuthService


def admin_required(fn):
    """
    관리자 권한이 필요한 API에 사용하는 데코레이터.

    사용 예:
    @admin_required
    def admin_api():
        ...

    처리 흐름:
    1. JWT 토큰 검증
    2. 토큰에서 user_id 추출
    3. DB에서 사용자 조회
    4. membership_type == "admin" 확인
    """

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()

        user = AuthService.get_user_by_id(int(user_id))

        if not user:
            return error_response("사용자를 찾을 수 없습니다.", 404)

        if user.membership_type != "admin":
            return error_response("관리자 권한이 필요합니다.", 403)

        return fn(*args, **kwargs)

    return wrapper