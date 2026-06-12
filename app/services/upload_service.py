"""
upload_service.py

영상 업로드 및 프레임 추출 서비스.

역할:
1. 업로드된 영상 파일 저장
2. DatasetVideo DB 저장
3. OpenCV로 프레임 추출
4. DatasetFrame DB 저장
5. 응답용 데이터 직렬화
"""

import os
import uuid
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

import cv2

from flask import current_app

from app.models.dataset_video import DatasetVideo
from app.models.dataset_frame import DatasetFrame
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.video_repository import VideoRepository
from app.repositories.frame_repository import FrameRepository


class UploadService:
    """
    영상 업로드 및 프레임 추출 서비스.
    """

    ALLOWED_VIDEO_EXTENSIONS = {"mp4", "avi", "mov", "mkv", "webm"}

    @staticmethod
    def upload_video(
        user_id: int,
        dataset_id: int,
        file: FileStorage,
        frame_interval_seconds: int = 3
    ) -> dict:
        """
        영상 업로드 후 프레임 추출까지 처리한다.
        """

        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise ValueError("데이터셋을 찾을 수 없습니다.")

        if not file or file.filename == "":
            raise ValueError("업로드할 영상 파일이 없습니다.")

        if not UploadService.is_allowed_video(file.filename):
            raise ValueError("지원하지 않는 영상 파일 형식입니다.")

        upload_root = current_app.config.get("UPLOAD_FOLDER", "uploads")

        video_dir = os.path.join(
            upload_root,
            "videos",
            str(dataset_id)
        )

        frame_dir = os.path.join(
            upload_root,
            "frames",
            str(dataset_id)
        )

        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(frame_dir, exist_ok=True)

        original_filename = secure_filename(file.filename)
        saved_filename = f"{uuid.uuid4().hex}_{original_filename}"
        video_path = os.path.join(video_dir, saved_filename)

        file.save(video_path)

        file_size = os.path.getsize(video_path)

        video_info = UploadService.get_video_info(video_path)

        video = DatasetVideo(
            dataset_id=dataset_id,
            file_name=original_filename,
            file_path=video_path,
            file_size=file_size,
            duration=video_info["duration"],
            fps=video_info["fps"],
            frame_count=video_info["frame_count"]
        )

        created_video = VideoRepository.create(video)

        frames = UploadService.extract_frames(
            video_id=created_video.id,
            video_path=video_path,
            frame_dir=frame_dir,
            fps=video_info["fps"],
            frame_interval_seconds=frame_interval_seconds
        )

        return {
            "video": UploadService.serialize_video(created_video),
            "extracted_frame_count": len(frames),
            "frames": [
                UploadService.serialize_frame(frame)
                for frame in frames
            ]
        }

    @staticmethod
    def extract_frames(
        video_id: int,
        video_path: str,
        frame_dir: str,
        fps: float,
        frame_interval_seconds: int = 3
    ) -> list[DatasetFrame]:
        """
        OpenCV를 이용해 일정 간격마다 프레임을 추출한다.
        """

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            raise ValueError("영상 파일을 열 수 없습니다.")

        if fps <= 0:
            fps = capture.get(cv2.CAP_PROP_FPS)

        if fps <= 0:
            fps = 30

        save_interval = int(fps * frame_interval_seconds)

        if save_interval <= 0:
            save_interval = 1

        frames: list[DatasetFrame] = []

        frame_index = 0
        saved_index = 0

        while True:
            success, frame = capture.read()

            if not success:
                break

            if frame_index % save_interval == 0:
                height, width = frame.shape[:2]

                frame_filename = f"video_{video_id}_frame_{saved_index:06d}.jpg"
                frame_path = os.path.join(frame_dir, frame_filename)

                cv2.imwrite(frame_path, frame)

                timestamp = frame_index / fps

                dataset_frame = DatasetFrame(
                    video_id=video_id,
                    frame_number=frame_index,
                    timestamp=timestamp,
                    file_name=frame_filename,
                    file_path=frame_path,
                    width=width,
                    height=height
                )

                frames.append(dataset_frame)
                saved_index += 1

            frame_index += 1

        capture.release()

        if not frames:
            raise ValueError("추출된 프레임이 없습니다.")

        return FrameRepository.create_all(frames)

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        영상의 fps, 전체 프레임 수, 길이를 조회한다.
        """

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            raise ValueError("영상 정보를 읽을 수 없습니다.")

        fps = capture.get(cv2.CAP_PROP_FPS)
        frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

        duration = None

        if fps and fps > 0:
            duration = frame_count / fps

        capture.release()

        return {
            "fps": fps,
            "frame_count": frame_count,
            "duration": duration
        }

    @staticmethod
    def is_allowed_video(filename: str) -> bool:
        """
        허용된 영상 확장자인지 검사한다.
        """

        if "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()

        return extension in UploadService.ALLOWED_VIDEO_EXTENSIONS

    @staticmethod
    def get_video_frames(video_id: int) -> list[dict]:
        """
        특정 영상의 프레임 목록 조회.
        """

        video = VideoRepository.find_by_id(video_id)

        if not video:
            raise ValueError("영상을 찾을 수 없습니다.")

        frames = FrameRepository.find_all_by_video_id(video_id)

        return [
            UploadService.serialize_frame(frame)
            for frame in frames
        ]

    @staticmethod
    def serialize_video(video: DatasetVideo) -> dict:
        return {
            "id": video.id,
            "dataset_id": video.dataset_id,
            "file_name": video.file_name,
            "file_path": video.file_path,
            "file_size": video.file_size,
            "duration": video.duration,
            "fps": video.fps,
            "frame_count": video.frame_count,
            "created_at": video.created_at.isoformat() if video.created_at else None,
            "updated_at": video.updated_at.isoformat() if video.updated_at else None,
        }

    @staticmethod
    def serialize_frame(frame: DatasetFrame) -> dict:
        return {
            "id": frame.id,
            "video_id": frame.video_id,
            "frame_number": frame.frame_number,
            "timestamp": frame.timestamp,
            "file_name": frame.file_name,
            "file_path": frame.file_path,
            "width": frame.width,
            "height": frame.height,
            "created_at": frame.created_at.isoformat() if frame.created_at else None,
            "updated_at": frame.updated_at.isoformat() if frame.updated_at else None,
        }

    @staticmethod
    def get_frame_by_id(frame_id: int):
        frame = FrameRepository.find_by_id(frame_id)

        if not frame:
            raise ValueError("프레임을 찾을 수 없습니다.")

        return frame