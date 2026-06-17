from flask import Flask
from flask_jwt_extended.exceptions import NoAuthorizationError
from jwt import ExpiredSignatureError, InvalidTokenError
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import Config
from app.extensions import db, migrate, jwt, cors
from app.common.responses import error_response
from app.common.exceptions import AppError


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": [
                    app.config["FRONTEND_URL"],
                    "http://localhost:5173",
                    "http://127.0.0.1:5173",
                ]
            }
        },
        supports_credentials=True
    )

    register_blueprints(app)
    register_error_handlers(app)
    register_jwt_handlers(jwt)

    return app


def register_blueprints(app):
    from app.routes.health_routes import health_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dataset_routes import dataset_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.oauth_routes import oauth_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.label_routes import label_bp
    from app.routes.classifier_routes import classifier_bp
    from app.routes.bounding_box_routes import bounding_box_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(label_bp)
    app.register_blueprint(classifier_bp)
    app.register_blueprint(bounding_box_bp)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(error):
        return error_response(
            message=error.message,
            status_code=error.status_code,
            details=error.details
        )

    @app.errorhandler(RequestEntityTooLarge)
    def handle_file_too_large(error):
        return error_response(
            message="업로드 가능한 파일 용량을 초과했습니다.",
            status_code=413
        )

    @app.errorhandler(NoAuthorizationError)
    def handle_no_authorization(error):
        return error_response(
            message="인증 토큰이 필요합니다.",
            status_code=401
        )

    @app.errorhandler(ExpiredSignatureError)
    def handle_expired_token(error):
        return error_response(
            message="인증 토큰이 만료되었습니다.",
            status_code=401
        )

    @app.errorhandler(InvalidTokenError)
    def handle_invalid_token(error):
        return error_response(
            message="유효하지 않은 인증 토큰입니다.",
            status_code=401
        )

    @app.errorhandler(404)
    def handle_not_found(error):
        return error_response(
            message="요청한 API를 찾을 수 없습니다.",
            status_code=404
        )

    @app.errorhandler(500)
    def handle_internal_error(error):
        return error_response(
            message="서버 내부 오류가 발생했습니다.",
            status_code=500
        )


def register_jwt_handlers(jwt_manager):
    @jwt_manager.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return error_response(
            message="인증 토큰이 만료되었습니다.",
            status_code=401
        )

    @jwt_manager.invalid_token_loader
    def invalid_token_callback(error):
        return error_response(
            message="유효하지 않은 인증 토큰입니다.",
            status_code=401,
            details=str(error)
        )

    @jwt_manager.unauthorized_loader
    def missing_token_callback(error):
        return error_response(
            message="인증 토큰이 필요합니다.",
            status_code=401,
            details=str(error)
        )