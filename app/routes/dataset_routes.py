"""
dataset_routes.py

데이터셋 프로젝트 관련 API 라우트.

제공 API:
- POST   /api/datasets
- GET    /api/datasets
- GET    /api/datasets/<dataset_id>
- DELETE /api/datasets/<dataset_id>

모든 API는 로그인한 사용자만 사용할 수 있다.
"""

from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError

from app.common.responses import success_response, error_response
from app.schemas.dataset_schema import CreateDatasetSchema
from app.services.dataset_service import DatasetService

dataset_bp = Blueprint("dataset", __name__, url_prefix="/api/datasets")


@dataset_bp.post("")
@jwt_required()
def create_dataset():
    """
    데이터셋 프로젝트 생성 API.

    요청 Header:
    Authorization: Bearer access_token

    요청 Body:
    {
        "name": "도로 화재 데이터셋",
        "description": "도로 및 터널 환경의 화재/연기 이미지 데이터셋"
    }
    """

    user_id = int(get_jwt_identity())

    json_data = request.get_json()

    if not json_data:
        return error_response("요청 데이터가 없습니다.", 400)

    schema = CreateDatasetSchema()

    try:
        data = schema.load(json_data)
    except ValidationError as err:
        return error_response(
            message="데이터셋 생성 요청 데이터가 올바르지 않습니다.",
            status_code=400,
            details=err.messages
        )

    try:
        dataset = DatasetService.create_dataset(
            user_id=user_id,
            name=data["name"],
            description=data.get("description")
        )

        return success_response(
            data=dataset,
            message="데이터셋 생성 성공",
            status_code=201
        )

    except Exception as e:
        return error_response(
            message="데이터셋 생성 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@dataset_bp.get("")
@jwt_required()
def get_my_datasets():
    """
    내 데이터셋 목록 조회 API.

    요청 Header:
    Authorization: Bearer access_token
    """

    user_id = int(get_jwt_identity())

    datasets = DatasetService.get_my_datasets(user_id)

    return success_response(
        data=datasets,
        message="내 데이터셋 목록 조회 성공"
    )


@dataset_bp.get("/<int:dataset_id>")
@jwt_required()
def get_dataset_detail(dataset_id: int):
    """
    데이터셋 상세 조회 API.

    요청 Header:
    Authorization: Bearer access_token

    Path Parameter:
    - dataset_id: 조회할 데이터셋 ID
    """

    user_id = int(get_jwt_identity())

    try:
        dataset = DatasetService.get_dataset_detail(
            dataset_id=dataset_id,
            user_id=user_id
        )

        return success_response(
            data=dataset,
            message="데이터셋 상세 조회 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="데이터셋 상세 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@dataset_bp.delete("/<int:dataset_id>")
@jwt_required()
def delete_dataset(dataset_id: int):
    """
    데이터셋 삭제 API.

    요청 Header:
    Authorization: Bearer access_token

    Path Parameter:
    - dataset_id: 삭제할 데이터셋 ID
    """

    user_id = int(get_jwt_identity())

    try:
        DatasetService.delete_dataset(
            dataset_id=dataset_id,
            user_id=user_id
        )

        return success_response(
            data=None,
            message="데이터셋 삭제 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="데이터셋 삭제 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )