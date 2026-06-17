"""
upload_service.py

영상 업로드 및 프레임 추출 서비스.

이번 버전의 핵심 기능:
1. 영상 업로드
2. 프레임 추출 간격 검증
3. 프레임 해상도 조절
4. 프레임 이미지 저장
5. auto_label=True일 경우 업로드 직후 자동 라벨링 실행
"""

import os
import uuid

import cv2
from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.common.exceptions import ValidationAppError, NotFoundAppError
from app.models.dataset_frame import DatasetFrame
from app.models.dataset_video import DatasetVideo
from app.repositories.dataset_repository import DatasetRepository
from app.repositories.frame_repository import FrameRepository
from app.repositories.video_repository import VideoRepository


class UploadService:
    """
    영상 업로드 및 프레임 추출 서비스.
    """

    @staticmethod
    def upload_video(
        user_id: int,
        dataset_id: int,
        file: FileStorage,
        frame_interval_seconds: int | None = None,
        target_width: int | None = None,
        auto_label: bool = False,
    ) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise NotFoundAppError("데이터셋을 찾을 수 없습니다.")

        UploadService.validate_upload_file(file)

        frame_interval_seconds = UploadService.validate_frame_interval(
            frame_interval_seconds
        )

        target_width = UploadService.validate_target_width(target_width)

        upload_root = current_app.config.get("UPLOAD_FOLDER", "uploads")

        video_dir = UploadService.make_safe_directory(
            upload_root,
            "videos",
            str(dataset_id)
        )

        frame_dir = UploadService.make_safe_directory(
            upload_root,
            "frames",
            str(dataset_id)
        )

        original_filename = secure_filename(file.filename)

        if not original_filename:
            raise ValidationAppError("파일명이 올바르지 않습니다.")

        saved_filename = f"{uuid.uuid4().hex}_{original_filename}"
        video_path = os.path.join(video_dir, saved_filename)

        try:
            file.save(video_path)
        except Exception as error:
            raise ValidationAppError(
                message="영상 파일 저장에 실패했습니다.",
                details=str(error)
            )

        if not os.path.exists(video_path):
            raise ValidationAppError("영상 파일이 정상적으로 저장되지 않았습니다.")

        file_size = os.path.getsize(video_path)

        if file_size <= 0:
            UploadService.remove_file_if_exists(video_path)
            raise ValidationAppError("비어 있는 영상 파일은 업로드할 수 없습니다.")

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

        try:
            frames = UploadService.extract_frames(
                video_id=created_video.id,
                video_path=video_path,
                frame_dir=frame_dir,
                fps=video_info["fps"],
                frame_interval_seconds=frame_interval_seconds,
                target_width=target_width,
            )

            auto_label_result = None

            if auto_label:
                from app.services.classifier_service import ClassifierService

                auto_label_result = ClassifierService.auto_label_dataset(
                    dataset_id=dataset_id,
                    user_id=user_id
                )

        except Exception:
            VideoRepository.delete(created_video)
            UploadService.remove_file_if_exists(video_path)
            raise

        return {
            "video": UploadService.serialize_video(created_video),
            "extracted_frame_count": len(frames),
            "target_width": target_width,
            "auto_label": auto_label,
            "auto_label_result": auto_label_result,
            "frames": [
                UploadService.serialize_frame(frame)
                for frame in frames
            ]
        }

    @staticmethod
    def validate_upload_file(file: FileStorage) -> None:
        if not file:
            raise ValidationAppError("업로드할 영상 파일이 없습니다.")

        if not file.filename:
            raise ValidationAppError("업로드할 영상 파일명이 없습니다.")

        if not UploadService.is_allowed_video(file.filename):
            raise ValidationAppError("지원하지 않는 영상 파일 형식입니다.")

    @staticmethod
    def validate_frame_interval(frame_interval_seconds: int | None) -> int:
        default_interval = current_app.config.get(
            "DEFAULT_FRAME_INTERVAL_SECONDS",
            3
        )

        min_interval = current_app.config.get(
            "MIN_FRAME_INTERVAL_SECONDS",
            1
        )

        max_interval = current_app.config.get(
            "MAX_FRAME_INTERVAL_SECONDS",
            60
        )

        if frame_interval_seconds is None:
            return default_interval

        try:
            interval = int(frame_interval_seconds)
        except (TypeError, ValueError):
            raise ValidationAppError("프레임 추출 간격은 숫자여야 합니다.")

        if interval < min_interval:
            raise ValidationAppError(
                f"프레임 추출 간격은 최소 {min_interval}초 이상이어야 합니다."
            )

        if interval > max_interval:
            raise ValidationAppError(
                f"프레임 추출 간격은 최대 {max_interval}초 이하여야 합니다."
            )

        return interval

    @staticmethod
    def validate_target_width(target_width: int | None) -> int | None:
        if target_width in (None, 0):
            return None

        try:
            width = int(target_width)
        except (TypeError, ValueError):
            raise ValidationAppError("해상도 값은 숫자여야 합니다.")

        allowed_widths = {640, 960, 1280}

        if width not in allowed_widths:
            raise ValidationAppError("지원하지 않는 해상도입니다.")

        return width

    @staticmethod
    def make_safe_directory(*paths: str) -> str:
        directory = os.path.join(*paths)
        os.makedirs(directory, exist_ok=True)

        if not os.path.isdir(directory):
            raise ValidationAppError("파일 저장 경로를 생성할 수 없습니다.")

        return directory

    @staticmethod
    def resize_frame(frame, target_width: int | None):
        if not target_width:
            return frame

        height, width = frame.shape[:2]

        if width <= target_width:
            return frame

        ratio = target_width / width
        target_height = int(height * ratio)

        return cv2.resize(
            frame,
            (target_width, target_height),
            interpolation=cv2.INTER_AREA
        )

    @staticmethod
    def extract_frames(
        video_id: int,
        video_path: str,
        frame_dir: str,
        fps: float,
        frame_interval_seconds: int = 3,
        target_width: int | None = None,
    ) -> list[DatasetFrame]:
        if not os.path.exists(video_path):
            raise ValidationAppError("영상 파일 경로가 존재하지 않습니다.")

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            capture.release()
            raise ValidationAppError("영상 파일을 열 수 없습니다.")

        if not fps or fps <= 0:
            fps = capture.get(cv2.CAP_PROP_FPS)

        if not fps or fps <= 0:
            fps = 30

        save_interval = int(fps * frame_interval_seconds)

        if save_interval <= 0:
            save_interval = 1

        frames: list[DatasetFrame] = []

        frame_index = 0
        saved_index = 0

        try:
            while True:
                success, frame = capture.read()

                if not success:
                    break

                if frame_index % save_interval == 0:
                    frame = UploadService.resize_frame(
                        frame=frame,
                        target_width=target_width
                    )

                    height, width = frame.shape[:2]

                    frame_filename = (
                        f"video_{video_id}_frame_{saved_index:06d}.jpg"
                    )
                    frame_path = os.path.join(frame_dir, frame_filename)

                    write_success = cv2.imwrite(frame_path, frame)

                    if not write_success:
                        raise ValidationAppError(
                            "프레임 이미지 저장에 실패했습니다."
                        )

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

        finally:
            capture.release()

        if not frames:
            raise ValidationAppError("추출된 프레임이 없습니다.")

        return FrameRepository.create_all(frames)

    @staticmethod
    def get_video_info(video_path: str) -> dict:
        if not os.path.exists(video_path):
            raise ValidationAppError("영상 파일 경로가 존재하지 않습니다.")

        capture = cv2.VideoCapture(video_path)

        if not capture.isOpened():
            capture.release()
            raise ValidationAppError("영상 정보를 읽을 수 없습니다.")

        try:
            fps = capture.get(cv2.CAP_PROP_FPS)
            frame_count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

            if frame_count <= 0:
                raise ValidationAppError("영상 프레임 정보를 읽을 수 없습니다.")

            duration = None

            if fps and fps > 0:
                duration = frame_count / fps

            return {
                "fps": fps,
                "frame_count": frame_count,
                "duration": duration
            }

        finally:
            capture.release()

    @staticmethod
    def is_allowed_video(filename: str) -> bool:
        if "." not in filename:
            return False

        extension = filename.rsplit(".", 1)[1].lower()

        allowed_extensions = current_app.config.get(
            "ALLOWED_VIDEO_EXTENSIONS",
            {"mp4", "avi", "mov", "mkv", "webm"}
        )

        return extension in allowed_extensions

    @staticmethod
    def get_video_frames(video_id: int) -> list[dict]:
        video = VideoRepository.find_by_id(video_id)

        if not video:
            raise NotFoundAppError("영상을 찾을 수 없습니다.")

        frames = FrameRepository.find_all_by_video_id(video_id)

        return [
            UploadService.serialize_frame(frame)
            for frame in frames
        ]

    @staticmethod
    def get_frame_by_id(frame_id: int) -> DatasetFrame:
        frame = FrameRepository.find_by_id(frame_id)

        if not frame:
            raise NotFoundAppError("프레임을 찾을 수 없습니다.")

        if not os.path.exists(frame.file_path):
            raise NotFoundAppError("프레임 이미지 파일을 찾을 수 없습니다.")

        return frame

    @staticmethod
    def remove_file_if_exists(file_path: str) -> None:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

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