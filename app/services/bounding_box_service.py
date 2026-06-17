from app.common.exceptions import NotFoundAppError, ValidationAppError
from app.models.bounding_box import BoundingBox
from app.repositories.bounding_box_repository import BoundingBoxRepository
from app.repositories.frame_repository import FrameRepository


class BoundingBoxService:
    """
    라벨링 박스 비즈니스 로직 계층.

    역할:
    - 수동 Bounding Box 생성
    - AI 자동 Bounding Box 생성
    - 프레임별 Bounding Box 조회
    - Bounding Box 수정
    - Bounding Box 삭제

    좌표 저장 방식:
    - x, y, width, height는 0~1 사이의 정규화 좌표로 저장한다.
    - 예: x=0.2, y=0.3, width=0.4, height=0.2
    """

    ALLOWED_LABELS = {
        "fire",
        "smoke",
        "carlight",
        "negative",
        "fire_smoke",
        "fire_smoke_carlight",
    }

    ALLOWED_SOURCES = {
        "manual",
        "ai",
    }

    @staticmethod
    def create_box(data: dict) -> dict:
        """
        Bounding Box 생성.

        수동 생성과 AI 자동 생성을 모두 지원한다.
        source가 없으면 기본값은 manual.
        is_verified가 없으면 manual은 True, ai는 False로 처리한다.
        """

        frame = FrameRepository.find_by_id(data["frame_id"])

        if not frame:
            raise NotFoundAppError("프레임을 찾을 수 없습니다.")

        label_name = data["label_name"]
        source = data.get("source", "manual")

        BoundingBoxService.validate_label_name(label_name)
        BoundingBoxService.validate_source(source)

        BoundingBoxService.validate_box_values(
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
        )

        is_verified = data.get("is_verified")

        if is_verified is None:
            is_verified = source == "manual"

        box = BoundingBox(
            frame_id=data["frame_id"],
            label_id=data.get("label_id"),
            label_name=label_name,
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            source=source,
            is_verified=is_verified,
        )

        created_box = BoundingBoxRepository.create(box)

        return BoundingBoxService.serialize_box(created_box)

    @staticmethod
    def get_frame_boxes(frame_id: int) -> list[dict]:
        frame = FrameRepository.find_by_id(frame_id)

        if not frame:
            raise NotFoundAppError("프레임을 찾을 수 없습니다.")

        boxes = BoundingBoxRepository.find_all_by_frame_id(frame_id)

        return [
            BoundingBoxService.serialize_box(box)
            for box in boxes
        ]

    @staticmethod
    def update_box(box_id: int, data: dict) -> dict:
        box = BoundingBoxRepository.find_by_id(box_id)

        if not box:
            raise NotFoundAppError("라벨링 박스를 찾을 수 없습니다.")

        if "label_name" in data:
            BoundingBoxService.validate_label_name(data["label_name"])
            box.label_name = data["label_name"]

        if "source" in data:
            BoundingBoxService.validate_source(data["source"])
            box.source = data["source"]

        for key in ["x", "y", "width", "height"]:
            if key in data:
                setattr(box, key, data[key])

        BoundingBoxService.validate_box_values(
            x=box.x,
            y=box.y,
            width=box.width,
            height=box.height,
        )

        if "is_verified" in data:
            box.is_verified = data["is_verified"]

        BoundingBoxRepository.commit()

        return BoundingBoxService.serialize_box(box)

    @staticmethod
    def delete_box(box_id: int) -> None:
        box = BoundingBoxRepository.find_by_id(box_id)

        if not box:
            raise NotFoundAppError("라벨링 박스를 찾을 수 없습니다.")

        BoundingBoxRepository.delete(box)

    @staticmethod
    def validate_label_name(label_name: str) -> None:
        if label_name not in BoundingBoxService.ALLOWED_LABELS:
            raise ValidationAppError("지원하지 않는 라벨입니다.")

    @staticmethod
    def validate_source(source: str) -> None:
        if source not in BoundingBoxService.ALLOWED_SOURCES:
            raise ValidationAppError("지원하지 않는 박스 출처입니다.")

    @staticmethod
    def validate_box_values(x: float, y: float, width: float, height: float) -> None:
        values = [x, y, width, height]

        if any(value < 0 or value > 1 for value in values):
            raise ValidationAppError("박스 좌표는 0부터 1 사이여야 합니다.")

        if width <= 0 or height <= 0:
            raise ValidationAppError("박스 너비와 높이는 0보다 커야 합니다.")

        if x + width > 1:
            raise ValidationAppError("박스가 이미지 가로 범위를 벗어났습니다.")

        if y + height > 1:
            raise ValidationAppError("박스가 이미지 세로 범위를 벗어났습니다.")

    @staticmethod
    def serialize_box(box: BoundingBox) -> dict:
        return {
            "id": box.id,
            "frame_id": box.frame_id,
            "label_id": box.label_id,
            "label_name": box.label_name,
            "x": box.x,
            "y": box.y,
            "width": box.width,
            "height": box.height,
            "source": box.source,
            "is_verified": box.is_verified,
            "created_at": box.created_at.isoformat() if box.created_at else None,
            "updated_at": box.updated_at.isoformat() if box.updated_at else None,
        }