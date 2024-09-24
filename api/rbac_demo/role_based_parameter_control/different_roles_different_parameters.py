from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from role_based_access_control import RoleBasedAccessControl
from models.user import UserInternal
from models.user.enums import UserRoles
from fastapi import Body
from typing import Annotated


class DifferentRolesDifferentParameters:

    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(
                    RoleBasedAccessControl(
                        allowed_roles={UserRoles.ADMIN, UserRoles.USER}
                    )
                )
            ],
            horse_ids: set[str] = Body()
    ):
        http_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="unauthorized parameters"
        )

        if user.user_role == UserRoles.USER:
            if not self.validate_horse_id_for_user(horse_ids=horse_ids):
                raise http_exception

        if user.user_role == UserRoles.ADMIN:
            if not self.validate_horse_id_for_admin(horse_ids=horse_ids):
                raise http_exception

        self.user = user
        self.horse_ids = horse_ids

    @staticmethod
    def validate_horse_id_for_user(horse_ids: set[str]):
        for horse_id in horse_ids:
            if horse_id not in {"1", "2", "3"}:
                return False

        return True

    @staticmethod
    def validate_horse_id_for_admin(horse_ids: set[str]):
        for horse_id in horse_ids:
            if horse_id not in {"4", "5", "6"}:
                return False

        return True
