from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors


def create_app():
    """
    Flask 애플리케이션 팩토리 함수.

    역할:
    1. Flask 앱 생성
    2. 환경설정 로드
    3. 확장 모듈 초기화
    4. Blueprint 등록
    """

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

    return app


def register_blueprints(app):
    """
    Blueprint 등록 함수.

    새 route 파일이 생기면 이곳에서 등록한다.
    """

    from app.routes.health_routes import health_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dataset_routes import dataset_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dataset_bp)