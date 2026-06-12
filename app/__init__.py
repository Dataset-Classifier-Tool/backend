from flask import Flask
from app.config import Config
from app.extensions import db, migrate, jwt, cors


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

    return app


def register_blueprints(app):
    from app.routes.health_routes import health_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.dataset_routes import dataset_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.oauth_routes import oauth_bp
    from app.routes.upload_routes import upload_bp
    from app.routes.label_routes import label_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dataset_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(oauth_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(label_bp)