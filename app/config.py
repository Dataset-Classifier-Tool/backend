import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    APP_NAME = os.getenv("APP_NAME", "Dataset Classifier Tool API")

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///dataset_classifier.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")

    MAX_CONTENT_LENGTH = int(
        os.getenv("MAX_CONTENT_LENGTH", 1024 * 1024 * 500)
    )

    ALLOWED_VIDEO_EXTENSIONS = {
        "mp4",
        "avi",
        "mov",
        "mkv",
        "webm",
    }

    MIN_FRAME_INTERVAL_SECONDS = 1
    MAX_FRAME_INTERVAL_SECONDS = 60
    DEFAULT_FRAME_INTERVAL_SECONDS = 3

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60))
    )

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 14))
    )

    KAKAO_CLIENT_ID = os.getenv("KAKAO_CLIENT_ID")
    KAKAO_CLIENT_SECRET = os.getenv("KAKAO_CLIENT_SECRET")
    KAKAO_REDIRECT_URI = os.getenv("KAKAO_REDIRECT_URI")

    NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
    NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
    NAVER_REDIRECT_URI = os.getenv("NAVER_REDIRECT_URI")

    OAUTH_FRONTEND_REDIRECT_URL = os.getenv(
        "OAUTH_FRONTEND_REDIRECT_URL",
        "http://localhost:5173/oauth/callback"
    )

    JSON_AS_ASCII = False