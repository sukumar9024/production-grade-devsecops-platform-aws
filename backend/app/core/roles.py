from typing import ClassVar


class Roles:
    ADMIN = "Admin"
    ENGINEER = "Engineer"
    VIEWER = "Viewer"

    ALL: ClassVar = {
        ADMIN,
        ENGINEER,
        VIEWER,
    }
