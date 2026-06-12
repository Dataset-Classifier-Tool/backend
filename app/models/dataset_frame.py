from app.extensions import db
from app.models.base import BaseModel


class DatasetFrame(db.Model, BaseModel):
    """
    영상에서 추출된 프레임 모델.
    """

    __tablename__ = "dataset_frames"

    id = db.Column(db.Integer, primary_key=True)

    video_id = db.Column(
        db.Integer,
        db.ForeignKey("dataset_videos.id"),
        nullable=False,
        index=True
    )

    frame_number = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.Float, nullable=True)

    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)

    width = db.Column(db.Integer, nullable=True)
    height = db.Column(db.Integer, nullable=True)

    video = db.relationship(
        "DatasetVideo",
        back_populates="frames"
    )

    labels = db.relationship(
        "Label",
        back_populates="frame",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<DatasetFrame id={self.id} frame_number={self.frame_number}>"