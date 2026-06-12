"""
video_repository.py

DatasetVideo 모델에 대한 DB 접근 계층.

역할:
- 업로드된 영상 저장
- 특정 데이터셋의 영상 목록 조회
- 영상 단건 조회
- 영상 삭제
"""

from app.extensions import db
from app.models.dataset_video import DatasetVideo


class VideoRepository:
    """
    DatasetVideo 테이블에 접근하는 Repository 클래스.
    """

    @staticmethod
    def create(video: DatasetVideo) -> DatasetVideo:
        db.session.add(video)
        db.session.commit()
        return video

    @staticmethod
    def find_by_id(video_id: int) -> DatasetVideo | None:
        return DatasetVideo.query.get(video_id)

    @staticmethod
    def find_by_id_and_dataset_id(
        video_id: int,
        dataset_id: int
    ) -> DatasetVideo | None:
        return (
            DatasetVideo.query
            .filter_by(id=video_id, dataset_id=dataset_id)
            .first()
        )

    @staticmethod
    def find_all_by_dataset_id(dataset_id: int) -> list[DatasetVideo]:
        return (
            DatasetVideo.query
            .filter_by(dataset_id=dataset_id)
            .order_by(DatasetVideo.created_at.desc())
            .all()
        )

    @staticmethod
    def delete(video: DatasetVideo) -> None:
        db.session.delete(video)
        db.session.commit()

    @staticmethod
    def commit() -> None:
        db.session.commit()

    @staticmethod
    def rollback() -> None:
        db.session.rollback()