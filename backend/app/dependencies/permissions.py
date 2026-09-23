from fastapi import Depends

from app.core.roles import Roles
from app.dependencies.rbac import require_roles
from app.models.user import User


def admin_only(
    current_user: User = Depends(
        require_roles(
            Roles.ADMIN
        )
    ),
) -> User:
    return current_user


def engineer_or_admin(
    current_user: User = Depends(
        require_roles(
            Roles.ADMIN,
            Roles.ENGINEER,
        )
    ),
) -> User:
    return current_user


def authenticated_user(
    current_user: User = Depends(
        require_roles(
            Roles.ADMIN,
            Roles.ENGINEER,
            Roles.VIEWER,
        )
    ),
) -> User:
    return current_user