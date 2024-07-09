from typing import Annotated, Any

from fastapi import Depends, HTTPException, status

from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

from ..models import EnlistHorseForRent

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER, UserRoles.CLUB})),
]


class BaseHorseRentingServiceValidator:
    http_exception = lambda message: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )

    def __init__(self, user: user_dependency) -> None:
        self.user = user

    @staticmethod
    def is_user_verified(user_details: UserInternal) -> bool:
        return user_details.otp_verified


class EnlistHorseForRentServiceValidator(BaseHorseRentingServiceValidator):
    def __init__(
        self, user: user_dependency, enlist_details: EnlistHorseForRent
    ) -> None:
        super().__init__(user)
        self.enlist_details = enlist_details

        if not self.is_user_verified(user_details=self.user):
            raise BaseHorseRentingServiceValidator.http_exception(
                message="User otp is not verified"
            )
