from app.extensions import db
from app.models.base import BaseModel


class User(db.Model, BaseModel):
    """
    서비스 사용자 모델.
    일반 회원, 프리미엄 회원, 관리자 권한을 구분한다.
    """

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)

    password_hash = db.Column(db.String(255), nullable=False)

    nickname = db.Column(db.String(100), nullable=False)

    membership_type = db.Column(
        db.String(20),
        nullable=False,
        default="free"
    )

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
        return f"<User id={self.id} email={self.email}>"