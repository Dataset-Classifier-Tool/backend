"""
auth_service.py

회원가입, 로그인, 현재 사용자 조회 등
인증 관련 핵심 비즈니스 로직을 처리하는 계층.

역할:
- 회원가입 처리
- 비밀번호 암호화
- 로그인 검증
- JWT access / refresh token 발급
- 현재 사용자 조회

Repository와 Route 사이의 중간 계층이다.
"""

from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token

from app.models.user import User
from app.repositories.user_repository import UserRepository


class AuthService:
    """
    인증 관련 서비스 클래스.
    """

    @staticmethod
    def register(email: str, password: str, nickname: str) -> dict:
        """
        회원가입 처리.

        처리 순서:
        1. 이메일 중복 확인
        2. 비밀번호 해시 처리
        3. User 객체 생성
        4. DB 저장
        5. 사용자 정보 반환

        Args:
            email: 사용자 이메일
            password: 평문 비밀번호
            nickname: 사용자 닉네임

        Returns:
            생성된 사용자 정보 dict

        Raises:
            ValueError: 이미 가입된 이메일인 경우
        """

        existing_user = UserRepository.find_by_email(email)

        if existing_user:
            raise ValueError("이미 가입된 이메일입니다.")

        password_hash = bcrypt.hash(password)

        user = User(
            email=email,
            password_hash=password_hash,
            nickname=nickname,
            membership_type="free",
            is_active=True
        )

        created_user = UserRepository.create(user)

        return AuthService.serialize_user(created_user)

    @staticmethod
    def login(email: str, password: str) -> dict:
        """
        로그인 처리.

        처리 순서:
        1. 이메일로 사용자 조회
        2. 사용자 존재 여부 확인
        3. 활성화 계정 여부 확인
        4. 비밀번호 검증
        5. access_token / refresh_token 발급
        6. 사용자 정보와 토큰 반환

        Args:
            email: 사용자 이메일
            password: 평문 비밀번호

        Returns:
            token과 user 정보가 담긴 dict

        Raises:
            ValueError: 로그인 실패 사유
        """

        user = UserRepository.find_by_email(email)

        if not user:
            raise ValueError("이메일 또는 비밀번호가 올바르지 않습니다.")

        if not user.is_active:
            raise ValueError("비활성화된 계정입니다.")

        if not bcrypt.verify(password, user.password_hash):
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
        """
        사용자 ID로 현재 사용자 조회.

        Args:
            user_id: 사용자 PK

        Returns:
            User 객체 또는 None
        """
        return UserRepository.find_by_id(user_id)

    @staticmethod
    def serialize_user(user: User) -> dict:
        """
        User 객체를 JSON 응답용 dict로 변환.

        비밀번호 해시는 절대 반환하지 않는다.
        """

        return {
            "id": user.id,
            "email": user.email,
            "nickname": user.nickname,
            "membership_type": user.membership_type,
            "is_active": user.is_active,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }