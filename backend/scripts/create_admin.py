import getpass

from sqlalchemy import select

from app.core.roles import Roles
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.role import Role
from app.models.user import User


def create_admin() -> None:
    email = input("Admin email: ").strip().lower()

    username = input("Admin username: ").strip().lower()

    full_name = input("Admin full name: ").strip()

    password = getpass.getpass("Admin password: ")

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters.")

    with SessionLocal() as db:
        existing_user = db.scalar(
            select(User).where((User.email == email) | (User.username == username))
        )

        if existing_user:
            raise ValueError("User already exists.")

        admin_role = db.scalar(select(Role).where(Role.name == Roles.ADMIN))

        if admin_role is None:
            raise RuntimeError(
                "Admin role is not configured. Run the role seed script first."
            )

        admin = User(
            email=email,
            username=username,
            full_name=full_name or None,
            password_hash=hash_password(password),
            role_id=admin_role.id,
            is_verified=True,
        )

        db.add(admin)
        db.commit()

        print(f"Admin created: {email}")


if __name__ == "__main__":
    create_admin()
