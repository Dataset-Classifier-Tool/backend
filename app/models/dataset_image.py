from app.extensions import db
from app.models.base import BaseModel


class DatasetImage(db.Model, BaseModel):
    """
    데이터셋에 포함되는 개별 이미지.
    영상에서 추출된 프레임도 이 모델에 저장한다.
    """

    __tablename__ = "dataset_images"

    id = db.Column(db.Integer, primary_key=True)

    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("datasets.id"),
        nullable=False,
        index=True
    )

    file_name = db.Column(db.String(255), nullable=False)

    file_path = db.Column(db.String(500), nullable=False)

    file_size = db.Column(db.Integer, nullable=True)

    width = db.Column(db.Integer, nullable=True)

    height = db.Column(db.Integer, nullable=True)

    dataset = db.relationship(
        "Dataset",
        back_populates="images"
    )

    labels = db.relationship(
        "Label",
        back_populates="image",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DatasetImage id={self.id} file_name={self.file_name}>"