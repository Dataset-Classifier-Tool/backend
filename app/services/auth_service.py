from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, create_refresh_token

from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    인증 서비스.

    담당:
    - 회원가입
    - 로그인
    - JWT 발급
    - 현재 사용자 조회
    """

    @staticmethod
    def register(name, birth_date, nickname, email, password) -> dict:
        existing_user = UserRepository.find_by_email(email)

        if existing_user:
            raise ValueError("이미 가입된 이메일입니다.")

        user = User(
            name=name,
            birth_date=birth_date,
            nickname=nickname,
            email=email,
            password_hash=generate_password_hash(password),
            membership_type="free",
            provider="local",
            provider_id=None,
            is_active=True
        )

        created_user = UserRepository.create(user)

        return AuthService.serialize_user(created_user)

    @staticmethod
    def login(email: str, password: str) -> dict:
        user = UserRepository.find_by_email(email)

        if not user:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise ValueError("비활성화된 계정입니다.")

        if user.provider != "local":
            raise ValueError("소셜 로그인 계정입니다.")

        if not user.password_hash:
            raise ValueError("비밀번호 정보가 없습니다.")

        if not check_password_hash(user.password_hash, password):
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        access_token = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": AuthService.serialize_user(user)
        }

    @staticmethod
    def get_user_by_id(user_id: int) -> User | None:
        return UserRepository.find_by_id(user_id)

    @staticmethod
    def serialize_user(user: User) -> dict:
        return {
            "id": user.id,
            "name": user.name,
            "birth_date": user.birth_date.isoformat() if user.birth_date else None,
            "nickname": user.nickname,
            "email": user.email,
            "membership_type": user.membership_type,
            "provider": user.provider,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }