from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.role import Role

DEFAULT_ROLES = [
    {
        "name": "Admin",
        "description": "Full administrative access",
    },
    {
        "name": "Engineer",
        "description": "Operational engineering access",
    },
    {
        "name": "Viewer",
        "description": "Read-only access",
    },
]


def seed_roles() -> None:
    with SessionLocal() as db:
        for role_data in DEFAULT_ROLES:
            existing_role = db.scalar(
                select(Role).where(Role.name == role_data["name"])
            )

            if existing_role:
                print(f"Role already exists: {role_data['name']}")
                continue

            role = Role(**role_data)

            db.add(role)

            print(f"Created role: {role_data['name']}")

        db.commit()


if __name__ == "__main__":
    seed_roles()
