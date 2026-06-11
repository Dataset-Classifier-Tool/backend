from app.extensions import db
from app.models.base import BaseModel


class Label(db.Model, BaseModel):
    """
    이미지에 부여된 라벨 정보.
    수동 라벨링과 AI 자동 분류 결과를 모두 저장한다.
    """

    __tablename__ = "labels"

    id = db.Column(db.Integer, primary_key=True)

    image_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset_images.id"),
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

    image = db.relationship(
        "DatasetImage",
        back_populates="labels"
    )

    def __repr__(self):
        return f"<Label id={self.id} label_name={self.label_name}>"