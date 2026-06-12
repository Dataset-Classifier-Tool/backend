from datetime import datetime
from app.extensions import db


class BaseModel:
    """
    모든 모델에서 공통으로 사용하는 기본 필드.
    """

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )