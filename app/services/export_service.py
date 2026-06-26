"""
export_service.py

라벨링된 데이터셋 Export 서비스.

현재 제공 기능:
1. 라벨별 이미지 ZIP 다운로드
2. YOLO 형식 ZIP 다운로드
3. YOLO Export 메타 정보 조회
"""

import os
import random
import tempfile
import zipfile
from datetime import datetime

from app.common.exceptions import NotFoundAppError, ValidationAppError
from app.repositories.dataset_repository import DatasetRepository


class ExportService:
    YOLO_CLASS_MAP = {
        "fire": 0,
        "smoke": 1,
        "carlight": 2,
    }

    YOLO_CLASS_NAMES = [
        "fire",
        "smoke",
        "carlight",
    ]

    YOLO_VAL_RATIO = 0.2
    YOLO_RANDOM_SEED = 42

    @staticmethod
    def export_labeled_images_zip(dataset_id: int, user_id: int) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id,
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

                label = labels[0]

                export_frames.append(
                    {
                        "frame": frame,
                        "label_name": label.label_name,
                    }
                )

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
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            ExportService.write_readme(
                zip_file=zip_file,
                dataset=dataset,
                export_frames=export_frames,
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
                    arcname=archive_name,
                )

        return {
            "zip_path": zip_path,
            "zip_filename": zip_filename,
            "export_frame_count": len(export_frames),
        }

    @staticmethod
    def export_yolo_dataset_zip(dataset_id: int, user_id: int) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        if not dataset:
            raise NotFoundAppError("데이터셋을 찾을 수 없습니다.")

        videos = getattr(dataset, "videos", [])

        if not videos:
            raise ValidationAppError("내보낼 영상이 없습니다.")

        export_items = ExportService.collect_yolo_export_items(dataset)

        if not export_items:
            raise ValidationAppError(
                "YOLO Export 가능한 Bounding Box가 없습니다. "
                "먼저 프레임에 fire/smoke/carlight 박스를 생성해주세요."
            )

        split_items = ExportService.split_train_val(export_items)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_dataset_name = ExportService.make_safe_name(dataset.name)

        zip_filename = (
            f"dataset_{dataset.id}_{safe_dataset_name}_yolo_{timestamp}.zip"
        )

        temp_dir = tempfile.gettempdir()
        zip_path = os.path.join(temp_dir, zip_filename)

        export_box_count = 0

        with zipfile.ZipFile(
            zip_path,
            mode="w",
            compression=zipfile.ZIP_DEFLATED,
        ) as zip_file:
            ExportService.write_yolo_metadata(
                zip_file=zip_file,
                dataset=dataset,
                train_count=len(split_items["train"]),
                val_count=len(split_items["val"]),
            )

            for split_name, items in split_items.items():
                for index, item in enumerate(items, start=1):
                    frame = item["frame"]
                    boxes = item["boxes"]

                    image_archive_name = ExportService.make_yolo_image_archive_name(
                        dataset_id=dataset.id,
                        frame=frame,
                        split_name=split_name,
                        index=index,
                    )

                    label_archive_name = ExportService.make_yolo_label_archive_name(
                        image_archive_name=image_archive_name,
                    )

                    yolo_label_text = ExportService.make_yolo_label_text(boxes)
                    export_box_count += len(boxes)

                    zip_file.write(
                        filename=frame.file_path,
                        arcname=image_archive_name,
                    )

                    zip_file.writestr(
                        label_archive_name,
                        yolo_label_text,
                    )

        return {
            "zip_path": zip_path,
            "zip_filename": zip_filename,
            "export_frame_count": len(export_items),
            "export_box_count": export_box_count,
        }

    @staticmethod
    def get_yolo_export_meta(dataset_id: int, user_id: int) -> dict:
        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        if not dataset:
            raise NotFoundAppError("데이터셋을 찾을 수 없습니다.")

        export_items = ExportService.collect_yolo_export_items(dataset)

        class_counts = {
            class_name: 0
            for class_name in ExportService.YOLO_CLASS_NAMES
        }

        export_box_count = 0

        for item in export_items:
            boxes = item["boxes"]

            for box in boxes:
                if box.label_name in class_counts:
                    class_counts[box.label_name] += 1
                    export_box_count += 1

        split_items = ExportService.split_train_val(export_items)

        return {
            "available": len(export_items) > 0,
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "export_frame_count": len(export_items),
            "export_box_count": export_box_count,
            "train_frame_count": len(split_items["train"]),
            "val_frame_count": len(split_items["val"]),
            "class_map": ExportService.YOLO_CLASS_MAP,
            "class_counts": class_counts,
        }

    @staticmethod
    def collect_yolo_export_items(dataset) -> list[dict]:
        export_items = []

        videos = getattr(dataset, "videos", [])

        for video in videos:
            frames = getattr(video, "frames", [])

            for frame in frames:
                if not frame.file_path or not os.path.exists(frame.file_path):
                    continue

                valid_boxes = ExportService.get_valid_yolo_boxes(frame)

                if not valid_boxes:
                    continue

                export_items.append(
                    {
                        "frame": frame,
                        "boxes": valid_boxes,
                    }
                )

        return export_items

    @staticmethod
    def get_valid_yolo_boxes(frame) -> list:
        bounding_boxes = getattr(frame, "bounding_boxes", [])

        valid_boxes = []

        for box in bounding_boxes:
            if box.label_name not in ExportService.YOLO_CLASS_MAP:
                continue

            if not ExportService.is_valid_normalized_box(box):
                continue

            valid_boxes.append(box)

        return valid_boxes

    @staticmethod
    def is_valid_normalized_box(box) -> bool:
        values = [box.x, box.y, box.width, box.height]

        if any(value is None for value in values):
            return False

        if box.width <= 0 or box.height <= 0:
            return False

        if box.x < 0 or box.y < 0:
            return False

        if box.x > 1 or box.y > 1:
            return False

        if box.width > 1 or box.height > 1:
            return False

        if box.x + box.width > 1:
            return False

        if box.y + box.height > 1:
            return False

        return True

    @staticmethod
    def make_yolo_label_text(boxes: list) -> str:
        lines = []

        for box in boxes:
            class_id = ExportService.YOLO_CLASS_MAP[box.label_name]

            x_center = box.x + (box.width / 2)
            y_center = box.y + (box.height / 2)

            line = (
                f"{class_id} "
                f"{x_center:.6f} "
                f"{y_center:.6f} "
                f"{box.width:.6f} "
                f"{box.height:.6f}"
            )

            lines.append(line)

        return "\n".join(lines) + "\n"

    @staticmethod
    def split_train_val(export_items: list[dict]) -> dict:
        items = export_items[:]

        random_generator = random.Random(ExportService.YOLO_RANDOM_SEED)
        random_generator.shuffle(items)

        if len(items) <= 1:
            return {
                "train": items,
                "val": [],
            }

        val_count = max(1, int(len(items) * ExportService.YOLO_VAL_RATIO))

        val_items = items[:val_count]
        train_items = items[val_count:]

        if not train_items:
            train_items = val_items
            val_items = []

        return {
            "train": train_items,
            "val": val_items,
        }

    @staticmethod
    def make_yolo_image_archive_name(
        dataset_id: int,
        frame,
        split_name: str,
        index: int,
    ) -> str:
        extension = ExportService.get_file_extension(frame.file_path)

        filename = (
            f"dataset_{dataset_id}_"
            f"frame_{frame.id}_"
            f"{index:06d}{extension}"
        )

        return f"dataset/images/{split_name}/{filename}"

    @staticmethod
    def make_yolo_label_archive_name(image_archive_name: str) -> str:
        label_archive_name = image_archive_name.replace(
            "dataset/images/",
            "dataset/labels/",
            1,
        )

        label_archive_name = os.path.splitext(label_archive_name)[0] + ".txt"

        return label_archive_name

    @staticmethod
    def write_yolo_metadata(
        zip_file,
        dataset,
        train_count: int,
        val_count: int,
    ) -> None:
        classes_text = "\n".join(ExportService.YOLO_CLASS_NAMES) + "\n"

        data_yaml = "\n".join(
            [
                "train: images/train",
                "val: images/val",
                "",
                f"nc: {len(ExportService.YOLO_CLASS_NAMES)}",
                "names:",
                *[
                    f"  {class_id}: {class_name}"
                    for class_name, class_id in ExportService.YOLO_CLASS_MAP.items()
                ],
                "",
            ]
        )

        readme_text = "\n".join(
            [
                "# YOLO Dataset Export",
                "",
                f"Dataset ID: {dataset.id}",
                f"Dataset Name: {dataset.name}",
                f"Description: {dataset.description or 'None'}",
                "",
                "## Classes",
                "",
                *[
                    f"- {class_id}: {class_name}"
                    for class_name, class_id in ExportService.YOLO_CLASS_MAP.items()
                ],
                "",
                "## Split",
                "",
                f"- train: {train_count}",
                f"- val: {val_count}",
                "",
                "## YOLO Label Format",
                "",
                "class_id x_center y_center width height",
                "",
                "All coordinates are normalized between 0 and 1.",
                "",
            ]
        )

        zip_file.writestr("dataset/classes.txt", classes_text)
        zip_file.writestr("dataset/data.yaml", data_yaml)
        zip_file.writestr("dataset/README.txt", readme_text)

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

        lines.extend(
            [
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
            ]
        )

        zip_file.writestr(
            "README.txt",
            "\n".join(lines),
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