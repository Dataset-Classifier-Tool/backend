import os

from sqlalchemy import inspect, text

from app import create_app
from app.extensions import db
from app.models import User, Dataset, DatasetVideo, DatasetFrame, Label, UsageLog
from app.seeds.seed_admin import seed_admin_user

app = create_app()


def check_database_connection():
    print("\n" + "=" * 60)
    print("[Database Check] 데이터베이스 연결 확인 시작")
    print("=" * 60)

    try:
        with app.app_context():
            db.session.execute(text("SELECT 1"))

            print("[OK] DB 연결 성공")
            print(f"[INFO] DB URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

            inspector = inspect(db.engine)
            table_names = inspector.get_table_names()

            if table_names:
                print("[INFO] 현재 생성된 테이블 목록:")
                for table_name in table_names:
                    print(f"  - {table_name}")
            else:
                print("[WARN] 현재 생성된 테이블이 없습니다.")
                print("       flask --app run.py init-db")

    except Exception as error:
        print("[ERROR] DB 연결 실패")
        print(f"[ERROR] 원인: {error}")

    finally:
        print("=" * 60)
        print("[Database Check] 데이터베이스 연결 확인 종료")
        print("=" * 60 + "\n")


@app.cli.command("init-db")
def init_db():
    with app.app_context():
        db.create_all()
        seed_admin_user()
        print("Database tables created successfully.")


@app.cli.command("seed-admin")
def seed_admin():
    with app.app_context():
        seed_admin_user()


@app.cli.command("show-tables")
def show_tables():
    with app.app_context():
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()

        if not table_names:
            print("No tables found.")
            return

        print("Current database tables:")
        for table_name in table_names:
            print(f"- {table_name}")


if __name__ == "__main__":
    check_database_connection()

    host = os.getenv("APP_HOST", "127.0.0.1")
    port = int(os.getenv("APP_PORT", 5001))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    app.run(host=host, port=port, debug=debug)