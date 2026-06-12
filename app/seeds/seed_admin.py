from werkzeug.security import generate_password_hash

from app.extensions import db
from app.models.user import User


def seed_admin_user():
    """
    개발용 관리자 계정 생성.

    이미 admin@dataset.com 계정이 있으면 새로 만들지 않는다.
    """

    admin_email = "admin@dataset.com"

    existing_admin = User.query.filter_by(email=admin_email).first()

    if existing_admin:
        print("[Seed] Admin user already exists.")
        return existing_admin

    admin = User(
        name="관리자",
        birth_date=None,
        nickname="Admin",
        email=admin_email,
        password_hash=generate_password_hash("admin1234!"),
        membership_type="admin",
        provider="local",
        provider_id=None,
        is_active=True
    )

    db.session.add(admin)
    db.session.commit()

    print("[Seed] Admin user created.")
    print("[Seed] email: admin@dataset.com")
    print("[Seed] password: admin1234!")

    return admin