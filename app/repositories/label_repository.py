"""
label_repository.py

Label 모델에 대한 DB 접근 계층.
"""

from app.extensions import db
from app.models.label import Label


class LabelRepository:
    """
    Label 테이블에 접근하는 Repository 클래스.
    """

    @staticmethod
    def create(label: Label) -> Label:
        db.session.add(label)
        db.session.commit()
        return label

    @staticmethod
    def find_by_id(label_id: int) -> Label | None:
        return Label.query.get(label_id)

    @staticmethod
    def find_first_by_frame_id(frame_id: int) -> Label | None:
        return (
            Label.query
            .filter_by(frame_id=frame_id)
            .order_by(Label.created_at.desc())
            .first()
        )

    @staticmethod
    def find_all_by_frame_id(frame_id: int) -> list[Label]:
        return (
            Label.query
            .filter_by(frame_id=frame_id)
            .order_by(Label.created_at.desc())
            .all()
        )

    @staticmethod
    def delete(label: Label) -> None:
        db.session.delete(label)
        db.session.commit()

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def rollback() -> None:
        db.session.rollback()