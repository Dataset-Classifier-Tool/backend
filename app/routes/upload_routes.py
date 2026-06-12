"""
upload_routes.py

영상 업로드 및 프레임 조회 API.

제공 API:
- POST /api/datasets/<dataset_id>/videos/upload
- GET  /api/videos/<video_id>/frames
"""

from flask import Blueprint, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.common.responses import success_response, error_response
from app.services.upload_service import UploadService


upload_bp = Blueprint("upload", __name__, url_prefix="/api")


@upload_bp.post("/datasets/<int:dataset_id>/videos/upload")
@jwt_required()
def upload_video(dataset_id: int):
    """
    영상 업로드 및 프레임 추출 API.

    요청 Header:
    Authorization: Bearer access_token

    요청 FormData:
    - file: 영상 파일
    - frame_interval_seconds: 프레임 추출 간격, 기본값 3초
    """

    user_id = int(get_jwt_identity())

    if "file" not in request.files:
        return error_response("업로드할 파일이 없습니다.", 400)

    file = request.files["file"]

    frame_interval_seconds = request.form.get(
        "frame_interval_seconds",
        default=3,
        type=int
    )

    try:
        result = UploadService.upload_video(
            user_id=user_id,
            dataset_id=dataset_id,
            file=file,
            frame_interval_seconds=frame_interval_seconds
        )

        return success_response(
            data=result,
            message="영상 업로드 및 프레임 추출 성공",
            status_code=201
        )

    except ValueError as e:
        return error_response(str(e), 400)

    except Exception as e:
        return error_response(
            message="영상 업로드 처리 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )


@upload_bp.get("/videos/<int:video_id>/frames")
@jwt_required()
def get_video_frames(video_id: int):
    """
    특정 영상의 프레임 목록 조회 API.
    """

    try:
        frames = UploadService.get_video_frames(video_id)

        return success_response(
            data=frames,
            message="프레임 목록 조회 성공"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="프레임 목록 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )

@upload_bp.get("/frames/<int:frame_id>/image")
@jwt_required()
def get_frame_image(frame_id: int):
    """
    프레임 이미지 파일 조회 API.
    """

    try:
        frame = UploadService.get_frame_by_id(frame_id)

        return send_file(
            frame.file_path,
            mimetype="image/jpeg"
        )

    except ValueError as e:
        return error_response(str(e), 404)

    except Exception as e:
        return error_response(
            message="프레임 이미지 조회 중 서버 오류가 발생했습니다.",
            status_code=500,
            details=str(e)
        )