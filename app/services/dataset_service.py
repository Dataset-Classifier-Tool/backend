"""
dataset_service.py

Dataset Project 관련 비즈니스 로직 계층.

역할:
- 데이터셋 생성
- 내 데이터셋 목록 조회
- 데이터셋 상세 조회
- 데이터셋 삭제
- 응답용 데이터 직렬화

Repository는 DB 작업만 담당하고,
Service는 권한/소유자 확인 같은 비즈니스 규칙을 담당한다.
"""

from app.models.dataset import Dataset
from app.repositories.dataset_repository import DatasetRepository


class DatasetService:
    """
    데이터셋 프로젝트 관련 서비스 클래스.
    """

    @staticmethod
    def create_dataset(user_id: int, name: str, description: str | None = None) -> dict:
        """
        데이터셋 프로젝트 생성.

        처리 흐름:
        1. 로그인 사용자 ID를 받는다.
        2. Dataset 객체를 만든다.
        3. DB에 저장한다.
        4. 응답용 dict로 변환해서 반환한다.

        Args:
            user_id: 현재 로그인한 사용자 ID
            name: 데이터셋 이름
            description: 데이터셋 설명

        Returns:
            생성된 데이터셋 정보 dict
        """

        dataset = Dataset(
            user_id=user_id,
            name=name,
            description=description
        )

        created_dataset = DatasetRepository.create(dataset)

        return DatasetService.serialize_dataset(created_dataset)

    @staticmethod
    def get_my_datasets(user_id: int) -> list[dict]:
        """
        현재 로그인 사용자의 데이터셋 목록 조회.

        Args:
            user_id: 현재 로그인한 사용자 ID

        Returns:
            데이터셋 정보 dict 리스트
        """

        datasets = DatasetRepository.find_all_by_user_id(user_id)

        return [
            DatasetService.serialize_dataset(dataset)
            for dataset in datasets
        ]

    @staticmethod
    def get_dataset_detail(dataset_id: int, user_id: int) -> dict:
        """
        데이터셋 상세 조회.

        중요:
        - dataset_id만으로 조회하지 않는다.
        - 반드시 user_id까지 같이 검사해서
          다른 사용자의 데이터셋을 볼 수 없게 막는다.

        Args:
            dataset_id: 조회할 데이터셋 ID
            user_id: 현재 로그인한 사용자 ID

        Returns:
            데이터셋 상세 정보 dict

        Raises:
            ValueError: 데이터셋이 없거나 권한이 없는 경우
        """

        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise ValueError("데이터셋을 찾을 수 없습니다.")

        return DatasetService.serialize_dataset(dataset, include_images=True)

    @staticmethod
    def delete_dataset(dataset_id: int, user_id: int) -> None:
        """
        데이터셋 삭제.

        중요:
        - 자기 데이터셋만 삭제 가능하다.
        - Dataset 모델의 relationship에 cascade가 설정되어 있으면
          연결된 이미지/라벨도 함께 삭제된다.

        Args:
            dataset_id: 삭제할 데이터셋 ID
            user_id: 현재 로그인한 사용자 ID

        Raises:
            ValueError: 데이터셋이 없거나 권한이 없는 경우
        """

        dataset = DatasetRepository.find_by_id_and_user_id(
            dataset_id=dataset_id,
            user_id=user_id
        )

        if not dataset:
            raise ValueError("데이터셋을 찾을 수 없습니다.")

        DatasetRepository.delete(dataset)

    @staticmethod
    def serialize_dataset(dataset: Dataset, include_images: bool = False) -> dict:
        """
        Dataset 객체를 JSON 응답용 dict로 변환.

        Args:
            dataset: Dataset 객체
            include_images: 이미지 목록 포함 여부

        Returns:
            JSON 변환 가능한 dict
        """

        data = {
            "id": dataset.id,
            "user_id": dataset.user_id,
            "name": dataset.name,
            "description": dataset.description,
            "image_count": len(dataset.images) if dataset.images is not None else 0,
            "created_at": dataset.created_at.isoformat() if dataset.created_at else None,
            "updated_at": dataset.updated_at.isoformat() if dataset.updated_at else None,
        }

        if include_images:
            data["images"] = [
                {
                    "id": image.id,
                    "file_name": image.file_name,
                    "file_path": image.file_path,
                    "file_size": image.file_size,
                    "width": image.width,
                    "height": image.height,
                    "created_at": image.created_at.isoformat() if image.created_at else None,
                    "updated_at": image.updated_at.isoformat() if image.updated_at else None,
                }
                for image in dataset.images
            ]

        return data