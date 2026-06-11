from flask import Blueprint
from app.common.responses import success_response

health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.get("/health")
def health_check():
    return success_response(
        data={
            "service": "Dataset Classifier Tool API",
            "status": "running"
        },
        message="API server is healthy"
    )