from app.extensions import db
from app.models.user import User
from app.services.auth_service import AuthService


class AdminService:
    """
    관리자 기능 서비스.

    담당:
    - 전체 회원 조회
    - 회원 등급 변경
    - 회원 활성/비활성 변경
    """

    @staticmethod
    def get_all_users() -> list[dict]:
        users = User.query.order_by(User.created_at.desc()).all()

        return [
            AuthService.serialize_user(user)
            for user in users
        ]

    @staticmethod
    def update_membership(user_id: int, membership_type: str) -> dict:
        user = User.query.get(user_id)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.membership_type = membership_type

        db.session.commit()

        return AuthService.serialize_user(user)

    @staticmethod
    def update_active(user_id: int, is_active: bool) -> dict:
        user = User.query.get(user_id)

        if not user:
            raise ValueError("사용자를 찾을 수 없습니다.")

        user.is_active = is_active

        db.session.commit()

        return AuthService.serialize_user(user)