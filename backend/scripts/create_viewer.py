"""Bootstrap a read-only smoke-test account without exposing a password in argv."""
import getpass

from fastapi import HTTPException
from pydantic import ValidationError

from app.db.session import SessionLocal
from app.schemas.user import UserCreate
from app.services.auth_service import AuthService


def main():
    try:
        payload = UserCreate(
            email=input("Viewer email: ").strip(),
            username=input("Viewer username: ").strip(),
            full_name="Deployment smoke account",
            password=getpass.getpass("Viewer password: "),
        )
        with SessionLocal() as db:
            AuthService.register_user(db, payload)
    except (ValidationError, HTTPException):
        raise SystemExit("Account creation failed: invalid values, duplicate account, or roles not seeded.") from None
    print("Viewer created. Store its matching identity/password in the application secret.")


if __name__ == "__main__":
    main()
