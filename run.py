import os

from app import create_app
from app.extensions import db
from app.models import User, Dataset, DatasetImage, Label, UsageLog

app = create_app()


@app.cli.command("init-db")
def init_db():
    """
    개발용 DB 초기화 명령어.
    사용법:
        flask --app run.py init-db
    """
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")


if __name__ == "__main__":
    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    app.run(host=host, port=port, debug=debug)