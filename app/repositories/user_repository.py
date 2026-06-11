"""
user_repository.py

User 모델에 대한 DB 접근을 전담하는 계층.

역할:
- 사용자를 이메일로 조회
- 사용자를 ID로 조회
- 신규 사용자 저장
- DB commit / rollback 처리

주의:
- Repository는 비즈니스 로직을 최대한 가지지 않는다.
- 비밀번호 검증, JWT 발급 같은 로직은 Service에서 처리한다.
"""

from app.extensions import db
from app.models.user import User


class UserRepository:
    """
    User 테이블에 접근하는 Repository 클래스.
    """

    @staticmethod
    def find_by_email(email: str) -> User | None:
        """
        이메일로 사용자 조회.

        사용처:
        - 회원가입 시 중복 이메일 검사
        - 로그인 시 사용자 존재 여부 확인

        Args:
            email: 사용자 이메일

        Returns:
            User 객체 또는 None
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def find_by_id(user_id: int) -> User | None:
        """
        ID로 사용자 조회.

        사용처:
        - JWT 토큰에서 꺼낸 user_id로 현재 사용자 조회

        Args:
            user_id: 사용자 PK

        Returns:
            User 객체 또는 None
        """
        return User.query.get(user_id)

    @staticmethod
    def create(user: User) -> User:
        """
        신규 사용자 저장.

        Args:
            user: 저장할 User 객체

        Returns:
            저장 완료된 User 객체
        """
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def commit():
        """
        DB 변경사항 저장.
        """
        db.session.commit()

    @staticmethod
    def rollback():
        """
        DB 작업 중 오류 발생 시 되돌리기.
        """
        db.session.rollback()