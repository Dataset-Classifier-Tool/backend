from app.extensions import db
from app.models.base import BaseModel


class UsageLog(db.Model, BaseModel):
    """
    회원별 사용량 기록.
    일반 회원 10회, 프리미엄 100회 제한 등에 사용한다.
    """

    __tablename__ = "usage_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    action = db.Column(db.String(50), nullable=False)

    user = db.relationship(
        "User",
        back_populates="usage_logs"
    )

    def __repr__(self):
        return f"<UsageLog id={self.id} action={self.action}>"