"""
export_routes.py

데이터셋 Export API 라우트.

제공 API:
- GET /api/datasets/<dataset_id>/export/zip
- GET /api/datasets/<dataset_id>/export/yolo
- GET /api/datasets/<dataset_id>/export/yolo/meta
"""

import os

from flask import Blueprint, after_this_request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.common.exceptions import AppError
from app.common.responses import error_response, success_response
from app.services.export_service import ExportService

export_bp = Blueprint("export", __name__, url_prefix="/api")


@export_bp.get("/datasets/<int:dataset_id>/export/zip")
@jwt_required()
def export_dataset_zip(dataset_id: int):
    user_id = int(get_jwt_identity())

    try:
        result = ExportService.export_labeled_images_zip(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        zip_path = result["zip_path"]
        zip_filename = result["zip_filename"]

        if not os.path.exists(zip_path):
            return error_response(
                message="Export ZIP 파일을 찾을 수 없습니다.",
                status_code=404,
            )

        @after_this_request
        def remove_temp_file(response):
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            except OSError:
                pass

            return response

        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=zip_filename,
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details,
        )

    except Exception as error:
        return error_response(
            message="데이터셋 Export 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error),
        )


@export_bp.get("/datasets/<int:dataset_id>/export/yolo")
@jwt_required()
def export_dataset_yolo(dataset_id: int):
    user_id = int(get_jwt_identity())

    try:
        result = ExportService.export_yolo_dataset_zip(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        zip_path = result["zip_path"]
        zip_filename = result["zip_filename"]

        if not os.path.exists(zip_path):
            return error_response(
                message="YOLO Export ZIP 파일을 찾을 수 없습니다.",
                status_code=404,
            )

        @after_this_request
        def remove_temp_file(response):
            try:
                if os.path.exists(zip_path):
                    os.remove(zip_path)
            except OSError:
                pass

            return response

        return send_file(
            zip_path,
            mimetype="application/zip",
            as_attachment=True,
            download_name=zip_filename,
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details,
        )

    except Exception as error:
        return error_response(
            message="YOLO Export 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error),
        )


@export_bp.get("/datasets/<int:dataset_id>/export/yolo/meta")
@jwt_required()
def get_yolo_export_meta(dataset_id: int):
    user_id = int(get_jwt_identity())

    try:
        result = ExportService.get_yolo_export_meta(
            dataset_id=dataset_id,
            user_id=user_id,
        )

        return success_response(
            data=result,
            message="YOLO Export 메타 정보를 조회했습니다.",
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details,
        )

    except Exception as error:
        return error_response(
            message="YOLO Export 메타 정보 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error),
        )