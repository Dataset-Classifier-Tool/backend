from app.extensions import db
from app.models.base import BaseModel


class BoundingBox(db.Model, BaseModel):
    """
    프레임 이미지 위에 그려진 라벨링 박스 모델.

    YOLO Export에 필요한 핵심 좌표를 저장한다.

    저장 방식:
    - x, y, width, height는 0~1 사이의 정규화 좌표로 저장한다.
    - 원본 이미지 크기와 무관하게 비율 기반으로 저장하기 위함이다.

    예:
    x = 0.25
    y = 0.30
    width = 0.40
    height = 0.20
    """

    __tablename__ = "bounding_boxes"

    id = db.Column(db.Integer, primary_key=True)

    frame_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset_frames.id"),
        nullable=False,
        index=True
    )

    label_id = db.Column(
        db.Integer,
        db.ForeignKey("labels.id"),
        nullable=True,
        index=True
    )

    label_name = db.Column(db.String(100), nullable=False)

    x = db.Column(db.Float, nullable=False)
    y = db.Column(db.Float, nullable=False)
    width = db.Column(db.Float, nullable=False)
    height = db.Column(db.Float, nullable=False)

    source = db.Column(
        db.String(20),
        nullable=False,
        default="manual"
    )

    is_verified = db.Column(
        db.Boolean,
        nullable=False,
        default=True
    )

    frame = db.relationship(
        "DatasetFrame",
        back_populates="bounding_boxes"
    )

    label = db.relationship(
        "Label",
        back_populates="bounding_boxes"
    )

    def __repr__(self):
        return f"<BoundingBox id={self.id} label_name={self.label_name}>"