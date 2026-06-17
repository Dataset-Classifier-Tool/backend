from app.extensions import db
from app.models.bounding_box import BoundingBox


class BoundingBoxRepository:
    """
    BoundingBox 테이블 DB 접근 계층.
    """

    @staticmethod
    def create(box: BoundingBox) -> BoundingBox:
        db.session.add(box)
        db.session.commit()
        return box

    @staticmethod
    def find_by_id(box_id: int) -> BoundingBox | None:
        return BoundingBox.query.get(box_id)

    @staticmethod
    def find_all_by_frame_id(frame_id: int) -> list[BoundingBox]:
        return (
            BoundingBox.query
            .filter_by(frame_id=frame_id)
            .order_by(BoundingBox.created_at.desc())
            .all()
        )

    @staticmethod
    def delete(box: BoundingBox) -> None:
        db.session.delete(box)
        db.session.commit()

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def rollback() -> None:
        db.session.rollback()