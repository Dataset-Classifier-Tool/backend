"""
frame_repository.py

DatasetFrame 모델에 대한 DB 접근 계층.

역할:
- 추출된 프레임 저장
- 특정 영상의 프레임 목록 조회
- 프레임 단건 조회
- 프레임 삭제
"""

from app.extensions import db
from app.models.dataset_frame import DatasetFrame


class FrameRepository:
    """
    DatasetFrame 테이블에 접근하는 Repository 클래스.
    """

    @staticmethod
    def create(frame: DatasetFrame) -> DatasetFrame:
        db.session.add(frame)
        db.session.commit()
        return frame

    @staticmethod
    def create_all(frames: list[DatasetFrame]) -> list[DatasetFrame]:
        db.session.add_all(frames)
        db.session.commit()
        return frames

    @staticmethod
    def find_by_id(frame_id: int) -> DatasetFrame | None:
        return DatasetFrame.query.get(frame_id)

    @staticmethod
    def find_all_by_video_id(video_id: int) -> list[DatasetFrame]:
        return (
            DatasetFrame.query
            .filter_by(video_id=video_id)
            .order_by(DatasetFrame.frame_number.asc())
            .all()
        )

    @staticmethod
    def delete(frame: DatasetFrame) -> None:
        db.session.delete(frame)
        db.session.commit()

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def rollback() -> None:
        db.session.rollback()