from app.extensions import db
from app.models.base import BaseModel


class Dataset(db.Model, BaseModel):
    """
    하나의 데이터셋 프로젝트.
    예: 도로 화재 데이터셋, 터널 연기 데이터셋.
    """

    __tablename__ = "datasets"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
        index=True
    )

    name = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=True)

    user = db.relationship(
        "User",
        back_populates="datasets"
    )

    images = db.relationship(
        "DatasetImage",
        back_populates="dataset",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Dataset id={self.id} name={self.name}>"