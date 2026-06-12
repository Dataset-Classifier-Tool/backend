from app.extensions import db
from app.models.base import BaseModel


class User(db.Model, BaseModel):
    """
    사용자 모델.

    회원가입 방식:
    - local: 일반 이메일/비밀번호 가입
    - kakao: 카카오 로그인
    - naver: 네이버 로그인

    회원 등급:
    - free: 일반 회원
    - premium: 프리미엄 회원
    - admin: 관리자
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    birth_date = db.Column(db.Date, nullable=True)

    nickname = db.Column(db.String(100), nullable=False)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=True)

    membership_type = db.Column(
        db.String(20),
        nullable=False,
        default="free"
    )

    provider = db.Column(
        db.String(20),
        nullable=False,
        default="local"
    )

    provider_id = db.Column(db.String(255), nullable=True)

    is_active = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    datasets = db.relationship(
        "Dataset",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    usage_logs = db.relationship(
        "UsageLog",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User id={self.id} email={self.email} membership={self.membership_type}>"