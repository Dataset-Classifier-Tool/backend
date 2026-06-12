"""
label_service.py

프레임 라벨링 비즈니스 로직 계층.

역할:
- 프레임에 라벨 생성
- 라벨 수정
- 라벨 삭제
- 라벨 응답 직렬화
"""

from app.models.label import Label
from app.repositories.frame_repository import FrameRepository
from app.repositories.label_repository import LabelRepository


class LabelService:
    """
    프레임 라벨링 서비스.
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
    def create_label(
            frame_id: int,
            label_name: str,
            confidence: float | None = None,
            source: str = "manual",
            is_verified: bool = True
    ) -> dict:
        frame = FrameRepository.find_by_id(frame_id)

        if not frame:
            raise ValueError("프레임을 찾을 수 없습니다.")

        LabelService.validate_label_name(label_name)
        LabelService.validate_source(source)

        existing_label = LabelRepository.find_first_by_frame_id(frame_id)

        if existing_label:
            existing_label.label_name = label_name
            existing_label.confidence = confidence
            existing_label.source = source
            existing_label.is_verified = is_verified

            LabelRepository.commit()

            return LabelService.serialize_label(existing_label)

        label = Label(
            frame_id=frame_id,
            label_name=label_name,
            confidence=confidence,
            source=source,
            is_verified=is_verified
        )

        created_label = LabelRepository.create(label)

        return LabelService.serialize_label(created_label)

    @staticmethod
    def update_label(
            label_id: int,
            label_name: str | None = None,
            confidence: float | None = None,
            source: str | None = None,
            is_verified: bool | None = None
    ) -> dict:
        label = LabelRepository.find_by_id(label_id)

        if not label:
            raise ValueError("라벨을 찾을 수 없습니다.")

        if label_name is not None:
            LabelService.validate_label_name(label_name)
            label.label_name = label_name

        if confidence is not None:
            label.confidence = confidence

        if source is not None:
            LabelService.validate_source(source)
            label.source = source

        if is_verified is not None:
            label.is_verified = is_verified

        LabelRepository.commit()

        return LabelService.serialize_label(label)

    @staticmethod
    def delete_label(label_id: int) -> None:
        label = LabelRepository.find_by_id(label_id)

        if not label:
            raise ValueError("라벨을 찾을 수 없습니다.")

        LabelRepository.delete(label)

    @staticmethod
    def validate_label_name(label_name: str) -> None:
        if label_name not in LabelService.ALLOWED_LABELS:
            raise ValueError("지원하지 않는 라벨입니다.")

    @staticmethod
    def validate_source(source: str) -> None:
        if source not in LabelService.ALLOWED_SOURCES:
            raise ValueError("지원하지 않는 라벨 출처입니다.")

    @staticmethod
    def serialize_label(label: Label) -> dict:
        return {
            "id": label.id,
            "frame_id": label.frame_id,
            "label_name": label.label_name,
            "confidence": label.confidence,
            "is_verified": label.is_verified,
            "source": label.source,
            "created_at": label.created_at.isoformat() if label.created_at else None,
            "updated_at": label.updated_at.isoformat() if label.updated_at else None,
        }
