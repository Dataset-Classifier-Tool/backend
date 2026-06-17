"""
upload_routes.py

영상 업로드 및 프레임 조회 API.

이번 버전의 핵심:
- frame_interval_seconds
- target_width
- auto_label
값을 FormData로 받아 UploadService에 전달한다.
"""

import os

from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.exceptions import AppError
from app.common.responses import success_response, error_response
from app.services.upload_service import UploadService


upload_bp = Blueprint("upload", __name__, url_prefix="/api")


@upload_bp.post("/datasets/<int:dataset_id>/videos/upload")
@jwt_required()
def upload_video(dataset_id: int):
    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return error_response(
            message="업로드할 파일이 없습니다.",
            status_code=400
        )

    file = request.files["file"]

    frame_interval_seconds = request.form.get(
        "frame_interval_seconds",
        default=None,
        type=int
    )

    target_width = request.form.get(
        "target_width",
        default=None,
        type=int
    )

    auto_label_raw = request.form.get(
        "auto_label",
        default="false"
    )

    auto_label = str(auto_label_raw).lower() == "true"

    try:
        result = UploadService.upload_video(
            user_id=user_id,
            dataset_id=dataset_id,
            file=file,
            frame_interval_seconds=frame_interval_seconds,
            target_width=target_width,
            auto_label=auto_label,
        )

        return success_response(
            data=result,
            message="영상 업로드 및 프레임 추출 성공",
            status_code=201
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )

    except Exception as error:
        return error_response(
            message="영상 업로드 처리 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error)
        )


@upload_bp.get("/videos/<int:video_id>/frames")
@jwt_required()
def get_video_frames(video_id: int):
    try:
        frames = UploadService.get_video_frames(video_id)

        return success_response(
            data=frames,
            message="프레임 목록 조회 성공"
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )

    except Exception as error:
        return error_response(
            message="프레임 목록 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error)
        )


@upload_bp.get("/frames/<int:frame_id>/image")
def get_frame_image(frame_id: int):
    try:
        frame = UploadService.get_frame_by_id(frame_id)

        image_path = os.path.abspath(frame.file_path)

        if not os.path.isfile(image_path):
            return error_response(
                message="프레임 이미지 파일을 찾을 수 없습니다.",
                status_code=404,
                details={
                    "frame_id": frame_id,
                    "saved_path": frame.file_path,
                    "absolute_path": image_path
                }
            )

        return send_file(
            image_path,
            mimetype="image/jpeg",
            as_attachment=False
        )

    except AppError as error:
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )

    except Exception as error:
        return error_response(
            message="프레임 이미지 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(error)
        )