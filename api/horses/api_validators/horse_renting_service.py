from typing import Annotated, List, Union

from fastapi import Depends, HTTPException, UploadFile, status

from data.dbapis.horse_renting_service.read_queries import (
    get_renting_enquiry_details_by_user_and_renting_service_id,
    get_renting_service_details_by_service_id,
)
from models.horse.horse_renting_service_internal import (
    HorseRentingServiceEnquiryInternalWithID,
    HorseRentingServiceInternalWithID,
)
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

from ..models import (
    EnlistHorseForRent,
    HorseRentEnquiry,
    UpdateHorseForRentServiceListing,
)

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
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseRentingServiceValidator.http_exception(
                message="renting service not owned by user"
            )

    @staticmethod
    def service_created_by_user(
        service_details: HorseRentingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id


class UpdateHorseForRentServiceListingValidator(BaseHorseRentingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        horse_renting_service_id: str,
        update_details: UpdateHorseForRentServiceListing,
    ) -> None:
        super().__init__(user)
        self.horse_renting_service_id = horse_renting_service_id
        self.update_details = update_details
        self.service_details = get_renting_service_details_by_service_id(
            service_id=horse_renting_service_id
        )

        if not self.service_created_by_user(
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseRentingServiceValidator.http_exception(
                message="renting service not owned by user"
            )

    @staticmethod
    def service_created_by_user(
        service_details: HorseRentingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id


class CreateRentEnquiryValidator(BaseHorseRentingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        enquiry_details: HorseRentEnquiry,
    ) -> None:
        super().__init__(user)

        self.service_details = get_renting_service_details_by_service_id(
            service_id=enquiry_details.horse_renting_service_id
        )

        if self.service_created_by_user(
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseRentingServiceValidator.http_exception(
                message="user cannot enquire about own listing"
            )

        self.old_enquiry_details = self.get_enquiry(
            user_id=self.user.id,
            renting_service_id=enquiry_details.horse_renting_service_id,
        )
        self.update_existing = True if self.old_enquiry_details else False

        self.enquiry_details = enquiry_details

    @staticmethod
    def get_enquiry(
        user_id: str, renting_service_id: str
    ) -> Union[HorseRentingServiceEnquiryInternalWithID, None]:
        return get_renting_enquiry_details_by_user_and_renting_service_id(
            user_id=user_id, renting_service_id=renting_service_id
        )

    @staticmethod
    def service_created_by_user(
        service_details: HorseRentingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id
