"""
dataset_service.py

Dataset Project 관련 비즈니스 로직 계층.

역할:
- 데이터셋 생성
- 내 데이터셋 목록 조회
- 데이터셋 상세 조회
- 데이터셋 삭제
- DatasetVideo / DatasetFrame 포함 응답 직렬화
"""

from app.models.dataset import Dataset
from app.repositories.dataset_repository import DatasetRepository


class DatasetService:
    """
    데이터셋 프로젝트 관련 서비스 클래스.
    """

    @staticmethod
    def create_dataset(user_id: int, name: str, description: str | None = None) -> dict:
        dataset = Dataset(
            user_id=user_id,
            name=name,
            description=description
        )

        created_dataset = DatasetRepository.create(dataset)

        return DatasetService.serialize_dataset(created_dataset)

    @staticmethod
    def get_my_datasets(user_id: int) -> list[dict]:
        datasets = DatasetRepository.find_all_by_user_id(user_id)

        return [
            DatasetService.serialize_dataset(dataset)
            for dataset in datasets
        ]

    @staticmethod
    def get_dataset_detail(dataset_id: int, user_id: int) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise ValueError("데이터셋을 찾을 수 없습니다.")

        return DatasetService.serialize_dataset(
            dataset,
            include_videos=True,
            include_frames=True
        )

    @staticmethod
    def delete_dataset(dataset_id: int, user_id: int) -> None:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise ValueError("데이터셋을 찾을 수 없습니다.")

        DatasetRepository.delete(dataset)

    @staticmethod
    def serialize_dataset(
        dataset: Dataset,
        include_videos: bool = False,
        include_frames: bool = False
    ) -> dict:
        videos = getattr(dataset, "videos", [])

        data = {
            "id": dataset.id,
            "user_id": dataset.user_id,
            "name": dataset.name,
            "description": dataset.description,
            "video_count": len(videos) if videos is not None else 0,
            "frame_count": sum(
                len(video.frames)
                for video in videos
            ) if videos is not None else 0,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        }

        if include_videos:
            data["videos"] = [
                DatasetService.serialize_video(
                    video,
                    include_frames=include_frames
                )
                for video in videos
            ]

        return data

    @staticmethod
    def serialize_video(video, include_frames: bool = False) -> dict:
        data = {
            "id": video.id,
            "dataset_id": video.dataset_id,
            "file_name": video.file_name,
            "file_path": video.file_path,
            "file_size": video.file_size,
            "duration": video.duration,
            "fps": video.fps,
            "frame_count": len(video.frames) if video.frames is not None else 0,
            "original_frame_count": video.frame_count,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "updated_at": video.updated_at.isoformat() if video.updated_at else None,
        }

        if include_frames:
            data["frames"] = [
                DatasetService.serialize_frame(frame)
                for frame in video.frames
            ]

        return data

    @staticmethod
    def serialize_frame(frame) -> dict:
        labels = getattr(frame, "labels", [])

        return {
            "id": frame.id,
            "video_id": frame.video_id,
            "frame_number": frame.frame_number,
            "timestamp": frame.timestamp,
            "file_name": frame.file_name,
            "file_path": frame.file_path,
            "width": frame.width,
            "height": frame.height,
            "labels": [
                {
                    "id": label.id,
                    "label_name": label.label_name,
                    "confidence": label.confidence,
                    "is_verified": label.is_verified,
                    "source": label.source,
                    "created_at": label.created_at.isoformat() if label.created_at else None,
                    "updated_at": label.updated_at.isoformat() if label.updated_at else None,
                }
                for label in labels
            ],
            "created_at": frame.created_at.isoformat() if frame.created_at else None,
            "updated_at": frame.updated_at.isoformat() if frame.updated_at else None,
        }