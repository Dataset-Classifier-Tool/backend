"""
export_service.py

라벨링된 데이터셋 Export 서비스.

현재 제공 기능:
- 라벨별 이미지 ZIP 다운로드

ZIP 구조:
dataset_1_export.zip
├── fire/
├── smoke/
├── carlight/
├── negative/
├── fire_smoke/
└── fire_smoke_carlight/

추후 확장:
- YOLO Export
- COCO Export
"""

import os
import zipfile
import tempfile
from datetime import datetime

from app.common.exceptions import NotFoundAppError, ValidationAppError
from app.repositories.dataset_repository import DatasetRepository


class ExportService:
    """
    데이터셋 Export 비즈니스 로직 계층.
    """

    @staticmethod
    def export_labeled_images_zip(dataset_id: int, user_id: int) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise NotFoundAppError("데이터셋을 찾을 수 없습니다.")

        videos = getattr(dataset, "videos", [])

        if not videos:
            raise ValidationAppError("내보낼 영상이 없습니다.")

        export_frames = []

        for video in videos:
            frames = getattr(video, "frames", [])

            for frame in frames:
                labels = getattr(frame, "labels", [])

                if not labels:
                    continue

                if not frame.file_path or not os.path.exists(frame.file_path):
                    continue

                # 현재 구조상 프레임당 대표 라벨 1개를 사용한다.
                # LabelService.create_label()이 기존 라벨을 갱신하는 방식이므로 대부분 1개만 존재한다.
                label = labels[0]

                export_frames.append({
                    "frame": frame,
                    "label_name": label.label_name,
                })

        if not export_frames:
            raise ValidationAppError("라벨링된 프레임이 없습니다.")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_dataset_name = ExportService.make_safe_name(dataset.name)

        zip_filename = f"dataset_{dataset.id}_{safe_dataset_name}_{timestamp}.zip"

        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, zip_filename)

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED
        ) as zip_file:
            ExportService.write_readme(
                zip_file=zip_file,
                dataset=dataset,
                export_frames=export_frames
            )

            for index, item in enumerate(export_frames, start=1):
                frame = item["frame"]
                label_name = item["label_name"]

                extension = ExportService.get_file_extension(frame.file_path)

                archive_name = (
                    f"{label_name}/"
                    f"dataset_{dataset.id}_"
                    f"frame_{frame.id}_"
                    f"{index:06d}{extension}"
                )

                zip_file.write(
                    filename=frame.file_path,
                    arcname=archive_name
                )

        return {
            "zip_path": zip_path,
            "zip_filename": zip_filename,
            "export_frame_count": len(export_frames),
        }

    @staticmethod
    def write_readme(zip_file, dataset, export_frames: list[dict]) -> None:
        label_counts = {}

        for item in export_frames:
            label_name = item["label_name"]
            label_counts[label_name] = label_counts.get(label_name, 0) + 1

        lines = [
            "# Dataset Classifier Tool Export",
            "",
            f"Dataset ID: {dataset.id}",
            f"Dataset Name: {dataset.name}",
            f"Description: {dataset.description or 'None'}",
            f"Exported Frame Count: {len(export_frames)}",
            "",
            "## Label Counts",
            "",
        ]

        for label_name, count in sorted(label_counts.items()):
            lines.append(f"- {label_name}: {count}")

        lines.extend([
            "",
            "## Directory Structure",
            "",
            "Images are grouped by label name.",
            "",
            "Example:",
            "",
            "fire/",
            "smoke/",
            "carlight/",
            "negative/",
            "",
        ])

        zip_file.writestr(
            "README.txt",
            "\n".join(lines)
        )

    @staticmethod
    def make_safe_name(name: str) -> str:
        if not name:
            return "dataset"

        safe_name = "".join(
            char if char.isalnum() else "_"
            for char in name
        )

        return safe_name[:50] or "dataset"

    @staticmethod
    def get_file_extension(file_path: str) -> str:
        _, extension = os.path.splitext(file_path)

        if not extension:
            return ".jpg"

        return extension.lower()