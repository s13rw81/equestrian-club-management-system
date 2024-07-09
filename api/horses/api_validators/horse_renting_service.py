from typing import Annotated, List

from fastapi import Depends, HTTPException, UploadFile, status

from data.dbapis.horse_renting_service.read_queries import (
    get_renting_service_details_by_service_id,
)
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


class UploadRentImageValidator(BaseHorseRentingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        horse_renting_service_id: str,
        files: List[UploadFile],
    ) -> None:
        super().__init__(user)
        self.horse_renting_service_id = horse_renting_service_id
        self.files = files
        self.service_details = get_renting_service_details_by_service_id(
            service_id=horse_renting_service_id
        )

        if not self.service_created_by_user(
            renting_service_id=horse_renting_service_id, creator_id=user.id
        ):
            raise BaseHorseRentingServiceValidator.http_exception(
                message="renting service not owned by user"
            )

    @staticmethod
    def service_created_by_user(renting_service_id, creator_id) -> bool:
        service_details = get_renting_service_details_by_service_id(
            service_id=renting_service_id
        )
        return service_details.provider.provider_id == creator_id
