"""
dataset_repository.py

Dataset 모델에 대한 DB 접근 계층.

역할:
- 데이터셋 프로젝트 생성
- 특정 사용자의 데이터셋 목록 조회
- 데이터셋 단건 조회
- 데이터셋 삭제

주의:
- Repository는 DB 작업만 담당한다.
- 권한 체크, 사용자 검증, 응답 형태 가공은 Service 계층에서 처리한다.
"""

from app.extensions import db
from app.models.dataset import Dataset


class DatasetRepository:
    """
    Dataset 테이블에 접근하는 Repository 클래스.
    """

    @staticmethod
    def create(dataset: Dataset) -> Dataset:
        """
        데이터셋 프로젝트 생성.

        Args:
            dataset: 저장할 Dataset 객체

        Returns:
            저장 완료된 Dataset 객체
        """
        db.session.add(dataset)
        db.session.commit()
        return dataset

    @staticmethod
    def find_all_by_user_id(user_id: int) -> list[Dataset]:
        """
        특정 사용자가 생성한 데이터셋 목록 조회.

        Args:
            user_id: 사용자 ID

        Returns:
            Dataset 객체 리스트
        """
        return (
            Dataset.query
            .filter_by(user_id=user_id)
            .order_by(Dataset.created_at.desc())
            .all()
        )

    @staticmethod
    def find_by_id(dataset_id: int) -> Dataset | None:
        """
        데이터셋 ID로 단건 조회.

        Args:
            dataset_id: 데이터셋 ID

        Returns:
            Dataset 객체 또는 None
        """
        return Dataset.query.get(dataset_id)

    @staticmethod
    def find_by_id_and_user_id(dataset_id: int, user_id: int) -> Dataset | None:
        """
        데이터셋 ID와 사용자 ID로 단건 조회.

        사용 목적:
        - 사용자가 자기 데이터셋만 접근하도록 제한하기 위함

        Args:
            dataset_id: 데이터셋 ID
            user_id: 사용자 ID

        Returns:
            Dataset 객체 또는 None
        """
        return (
            Dataset.query
            .filter_by(id=dataset_id, user_id=user_id)
            .first()
        )

    @staticmethod
    def delete(dataset: Dataset) -> None:
        """
        데이터셋 삭제.

        Dataset 모델에 cascade 옵션이 설정되어 있으므로
        나중에 DatasetImage가 연결되어 있으면 함께 삭제된다.

        Args:
            dataset: 삭제할 Dataset 객체
        """
        db.session.delete(dataset)
        db.session.commit()

    @staticmethod
    def commit():
        """
        DB 변경사항 저장.
        """
        db.session.commit()

    @staticmethod
    def rollback():
        """
        DB 작업 중 오류 발생 시 되돌리기.
        """
        db.session.rollback()