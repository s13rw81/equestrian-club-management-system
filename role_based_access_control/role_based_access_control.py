from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from logic.auth import get_current_user
from typing import Annotated
from models.user import UserInternal
from logging_config import log
from models.user.enums import UserRoles


class RoleBasedAccessControl:

    def __init__(self, allowed_roles: set[UserRoles]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[UserInternal, Depends(get_current_user)]) -> UserInternal:
        log.info(f"inside RoleBasedAccessControl; allowed_roles={self.allowed_roles}; user={user}")

        if user.user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"the user must have the following roles to access this route: {self.allowed_roles}"
            )

        return user
