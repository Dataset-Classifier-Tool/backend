from app.extensions import db
from app.models.base import BaseModel


class DatasetVideo(db.Model, BaseModel):
    """
    업로드된 원본 영상 모델.
    하나의 Dataset은 여러 개의 영상을 가질 수 있다.
    """

    __tablename__ = "dataset_videos"

    id = db.Column(db.Integer, primary_key=True)

    dataset_id = db.Column(
        db.Integer,
        db.ForeignKey("datasets.id"),
        nullable=False,
        index=True
    )

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=True)

    duration = db.Column(db.Float, nullable=True)
    fps = db.Column(db.Float, nullable=True)
    frame_count = db.Column(db.Integer, nullable=True)

    dataset = db.relationship(
        "Dataset",
        back_populates="videos"
    )

    frames = db.relationship(
        "DatasetFrame",
        back_populates="video",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DatasetVideo id={self.id} file_name={self.file_name}>"