"""
classifier_service.py

AI 자동 라벨링 + 자동 Bounding Box 생성 서비스.

현재 단계:
- 실제 학습 모델이 붙기 전까지 OpenCV 기반 휴리스틱 사용
- 프레임 이미지 색상 특징으로 라벨 예측
- 색상 마스크와 contour 기반으로 자동 Bounding Box 생성
- 추후 YOLO / RT-DETR / Keras 모델을 붙일 때는 predict_frame() 내부만 교체하면 됨

자동화 흐름:
Dataset
 → Video
 → Frame
 → 이미지 분석
 → Label(source="ai", confidence=..., is_verified=False) 저장
 → BoundingBox(source="ai", is_verified=False) 자동 저장
"""

import os

import cv2
import numpy as np

from app.common.exceptions import NotFoundAppError, ValidationAppError
from app.repositories.dataset_repository import DatasetRepository
from app.services.bounding_box_service import BoundingBoxService
from app.services.label_service import LabelService


class ClassifierService:
    """
    데이터셋 자동 라벨링 서비스.
    """

    @staticmethod
    def auto_label_dataset(dataset_id: int, user_id: int) -> dict:
        """
        특정 데이터셋의 모든 프레임을 자동 라벨링한다.

        처리 내용:
        1. 데이터셋 소유자 검증
        2. 데이터셋 내 모든 영상/프레임 순회
        3. 프레임 이미지 예측
        4. Label 자동 생성
        5. Bounding Box 자동 생성
        6. 라벨별 카운트 반환
        """

        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise NotFoundAppError("데이터셋을 찾을 수 없습니다.")

        videos = getattr(dataset, "videos", [])

        if not videos:
            raise ValidationAppError("자동 라벨링할 영상이 없습니다.")

        label_counts = {
            "fire": 0,
            "smoke": 0,
            "carlight": 0,
            "negative": 0,
            "fire_smoke": 0,
            "fire_smoke_carlight": 0,
        }

        total_frames = 0
        labeled_frames = 0
        failed_frames = 0
        created_box_count = 0
        results = []

        for video in videos:
            frames = getattr(video, "frames", [])

            for frame in frames:
                total_frames += 1

                try:
                    prediction = ClassifierService.predict_frame(frame.file_path)

                    label = LabelService.create_label(
                        frame_id=frame.id,
                        label_name=prediction["label_name"],
                        confidence=prediction["confidence"],
                        source="ai",
                        is_verified=False
                    )

                    label_counts[prediction["label_name"]] += 1
                    labeled_frames += 1

                    created_boxes = []

                    for box in prediction.get("boxes", []):
                        created_box = BoundingBoxService.create_box({
                            "frame_id": frame.id,
                            "label_id": label["id"],
                            "label_name": prediction["label_name"],
                            "x": box["x"],
                            "y": box["y"],
                            "width": box["width"],
                            "height": box["height"],
                            "source": "ai",
                            "is_verified": False,
                        })

                        created_boxes.append(created_box)
                        created_box_count += 1

                    results.append({
                        "frame_id": frame.id,
                        "frame_number": frame.frame_number,
                        "label": label,
                        "prediction": prediction,
                        "boxes": created_boxes,
                    })

                except Exception as error:
                    failed_frames += 1

                    results.append({
                        "frame_id": frame.id,
                        "frame_number": frame.frame_number,
                        "error": str(error)
                    })

        return {
            "dataset_id": dataset.id,
            "total_frames": total_frames,
            "labeled_frames": labeled_frames,
            "failed_frames": failed_frames,
            "created_box_count": created_box_count,
            "label_counts": label_counts,
            "results": results
        }

    @staticmethod
    def predict_frame(image_path: str) -> dict:
        """
        단일 프레임 이미지 예측.

        반환:
        {
            "label_name": "fire",
            "confidence": 0.82,
            "scores": {...},
            "boxes": [
                {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4}
            ]
        }
        """

        if not image_path or not os.path.exists(image_path):
            raise NotFoundAppError("프레임 이미지 파일을 찾을 수 없습니다.")

        image = cv2.imread(image_path)

        if image is None:
            raise ValidationAppError("프레임 이미지를 읽을 수 없습니다.")

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        fire_score = ClassifierService.calculate_fire_score(hsv)
        smoke_score = ClassifierService.calculate_smoke_score(hsv)
        carlight_score = ClassifierService.calculate_carlight_score(hsv)

        FIRE_THRESHOLD = 0.22
        SMOKE_THRESHOLD = 0.35
        CARLIGHT_THRESHOLD = 0.45

        if fire_score >= FIRE_THRESHOLD and smoke_score >= SMOKE_THRESHOLD:
            label_name = "fire_smoke"
            confidence = max(fire_score, smoke_score)

            fire_boxes = ClassifierService.extract_fire_boxes(image, hsv)
            smoke_boxes = ClassifierService.extract_smoke_boxes(image, hsv)
            boxes = ClassifierService.merge_boxes(fire_boxes + smoke_boxes)

        elif smoke_score >= SMOKE_THRESHOLD:
            label_name = "smoke"
            confidence = smoke_score
            boxes = ClassifierService.extract_smoke_boxes(image, hsv)

        elif fire_score >= FIRE_THRESHOLD:
            label_name = "fire"
            confidence = fire_score
            boxes = ClassifierService.extract_fire_boxes(image, hsv)

        elif carlight_score >= CARLIGHT_THRESHOLD:
            label_name = "carlight"
            confidence = carlight_score
            boxes = ClassifierService.extract_carlight_boxes(image, hsv)

        else:
            label_name = "negative"
            confidence = 0.70
            boxes = []

        return {
            "label_name": label_name,
            "confidence": round(float(confidence), 4),
            "scores": {
                "fire": round(float(fire_score), 4),
                "smoke": round(float(smoke_score), 4),
                "carlight": round(float(carlight_score), 4),
                "negative": 0.15,
            },
            "boxes": boxes,
        }

    @staticmethod
    def calculate_fire_score(hsv) -> float:
        """
        화재 색상 점수 계산.
        붉은색, 주황색 계열 픽셀 비율을 기반으로 한다.
        """

        fire_mask = ClassifierService.create_fire_mask(hsv)
        ratio = np.count_nonzero(fire_mask) / fire_mask.size

        return min(ratio * 8, 1.0)

    @staticmethod
    def calculate_smoke_score(hsv) -> float:
        """
        연기 색상 점수 계산.
        저채도 회색 영역 비율을 기반으로 한다.
        """

        smoke_mask = ClassifierService.create_smoke_mask(hsv)
        ratio = np.count_nonzero(smoke_mask) / smoke_mask.size

        return min(ratio * 2.5, 1.0)

    @staticmethod
    def calculate_carlight_score(hsv) -> float:
        """
        차량 등화류 점수 계산.
        밝은 흰색/노란색 영역 비율을 기반으로 한다.
        """

        carlight_mask = ClassifierService.create_carlight_mask(hsv)
        ratio = np.count_nonzero(carlight_mask) / carlight_mask.size

        return min(ratio * 6, 1.0)

    @staticmethod
    def create_fire_mask(hsv):
        """
        화재 후보 영역 마스크 생성.
        """

        lower_red1 = np.array([0, 80, 80])
        upper_red1 = np.array([15, 255, 255])

        lower_red2 = np.array([160, 80, 80])
        upper_red2 = np.array([179, 255, 255])

        lower_orange = np.array([16, 80, 100])
        upper_orange = np.array([35, 255, 255])

        mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

        return mask_red1 | mask_red2 | mask_orange

    @staticmethod
    def create_smoke_mask(hsv):
        """
        연기 후보 영역 마스크 생성.
        """

        lower_smoke = np.array([0, 0, 80])
        upper_smoke = np.array([179, 60, 230])

        return cv2.inRange(hsv, lower_smoke, upper_smoke)

    @staticmethod
    def create_carlight_mask(hsv):
        """
        차량 등화류 후보 영역 마스크 생성.
        """

        lower_bright = np.array([0, 0, 220])
        upper_bright = np.array([179, 80, 255])

        white_mask = cv2.inRange(hsv, lower_bright, upper_bright)

        lower_yellow = np.array([18, 60, 180])
        upper_yellow = np.array([40, 255, 255])

        yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)

        return white_mask | yellow_mask

    @staticmethod
    def extract_fire_boxes(image, hsv) -> list[dict]:
        """
        화재 후보 영역 Bounding Box 추출.
        """

        mask = ClassifierService.create_fire_mask(hsv)

        return ClassifierService.contours_to_boxes(
            mask=mask,
            min_area_ratio=0.0008,
            max_boxes=5
        )

    @staticmethod
    def extract_smoke_boxes(image, hsv) -> list[dict]:
        """
        연기 후보 영역 Bounding Box 추출.
        """

        mask = ClassifierService.create_smoke_mask(hsv)

        return ClassifierService.contours_to_boxes(
            mask=mask,
            min_area_ratio=0.002,
            max_boxes=5
        )

    @staticmethod
    def extract_carlight_boxes(image, hsv) -> list[dict]:
        """
        차량 등화류 후보 영역 Bounding Box 추출.
        """

        mask = ClassifierService.create_carlight_mask(hsv)

        return ClassifierService.contours_to_boxes(
            mask=mask,
            min_area_ratio=0.0003,
            max_boxes=5
        )

    @staticmethod
    def contours_to_boxes(
        mask,
        min_area_ratio: float = 0.001,
        max_boxes: int = 5
    ) -> list[dict]:
        """
        마스크에서 contour를 찾아 정규화된 Bounding Box로 변환한다.
        """

        height, width = mask.shape[:2]
        image_area = width * height
        min_area = image_area * min_area_ratio

        kernel = np.ones((5, 5), np.uint8)

        cleaned_mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        cleaned_mask = cv2.morphologyEx(cleaned_mask, cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(
            cleaned_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        boxes = []

        sorted_contours = sorted(
            contours,
            key=cv2.contourArea,
            reverse=True
        )

        for contour in sorted_contours:
            area = cv2.contourArea(contour)

            if area < min_area:
                continue

            x, y, w, h = cv2.boundingRect(contour)

            if w <= 0 or h <= 0:
                continue

            box = {
                "x": round(x / width, 6),
                "y": round(y / height, 6),
                "width": round(w / width, 6),
                "height": round(h / height, 6),
            }

            boxes.append(box)

            if len(boxes) >= max_boxes:
                break

        return boxes

    @staticmethod
    def merge_boxes(boxes: list[dict]) -> list[dict]:
        """
        fire_smoke처럼 여러 마스크에서 나온 박스를 하나의 리스트로 정리한다.

        현재는 단순 중복 제거만 수행한다.
        추후 IoU 기반 병합으로 개선 가능하다.
        """

        unique_boxes = []
        seen = set()

        for box in boxes:
            key = (
                round(box["x"], 3),
                round(box["y"], 3),
                round(box["width"], 3),
                round(box["height"], 3),
            )

            if key in seen:
                continue

            seen.add(key)
            unique_boxes.append(box)

        return unique_boxes[:8]