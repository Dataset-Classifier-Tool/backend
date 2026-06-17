"""
classifier_routes.py

AI 자동 라벨링 API 라우트.

제공 API:
- POST /api/datasets/<dataset_id>/auto-label
"""

from flask import Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.exceptions import AppError
from app.common.responses import success_response, error_response
from app.services.classifier_service import ClassifierService


classifier_bp = Blueprint("classifier", __name__, url_prefix="/api")


@classifier_bp.post("/datasets/<int:dataset_id>/auto-label")
@jwt_required()
def auto_label_dataset(dataset_id: int):
    """
    데이터셋 전체 자동 라벨링 API.
    """

    user_id = int(get_jwt_identity())

    try:
        result = ClassifierService.auto_label_dataset(
            dataset_id=dataset_id,
            user_id=user_id
        )

        return success_response(
            data=result,
            message="AI 자동 라벨링 완료"
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )

    except Exception as error:
        return error_response(
            message="AI 자동 라벨링 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error)
        )