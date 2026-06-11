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

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret-key")

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", 60))
    )

    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", 14))
    )

    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    JSON_AS_ASCII = False