from app.extensions import db
from app.models.base import BaseModel


class Label(db.Model, BaseModel):
    """
    프레임에 부여된 라벨 정보.
    AI 자동 분류 결과와 사용자의 수동 검수 결과를 모두 저장한다.
    """

    __tablename__ = "labels"

    id = db.Column(db.Integer, primary_key=True)

    frame_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset_frames.id"),
        nullable=False,
        index=True
    )

    label_name = db.Column(db.String(100), nullable=False)

    confidence = db.Column(db.Float, nullable=True)

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=False
    )

    source = db.Column(
        db.String(20),
        nullable=False,
        default="manual"
    )

    frame = db.relationship(
        "DatasetFrame",
        back_populates="labels"
    )

    def __repr__(self):
        return f"<Label id={self.id} label_name={self.label_name}>"