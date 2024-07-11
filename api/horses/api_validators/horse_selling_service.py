from typing import Annotated, List, Union

from fastapi import Depends, HTTPException, UploadFile, status

from data.dbapis.horse_selling_service.read_queries import (
    get_selling_enquiry_details_by_enquiry_id,
    get_selling_enquiry_details_by_user_and_selling_service_id,
    get_selling_service_details_by_service_id,
)
from models.horse.horse_selling_service_internal import (
    HorseSellingServiceEnquiryInternalWithID,
    HorseSellingServiceInternalWithID,
)
from models.user import UserInternal, UserRoles
from models.user.enums import UserRoles
from models.user.user_internal import UserInternal
from role_based_access_control import RoleBasedAccessControl

from ..models import (
    EnlistHorseForSell,
    HorseSellEnquiry,
    UpdateHorseForSellServiceListing,
    UpdateHorseSellEnquiry,
)

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER, UserRoles.CLUB})),
]
user_admin_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER, UserRoles.ADMIN})),
]


class BaseHorseSellingServiceValidator:
    http_exception = lambda message: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )

    def __init__(self, user: user_dependency) -> None:
        self.user = user

    @staticmethod
    def is_user_verified(user_details: UserInternal) -> bool:
        return user_details.otp_verified


class EnlistHorseForSellServiceValidator(BaseHorseSellingServiceValidator):
    def __init__(
        self, user: user_dependency, enlist_details: EnlistHorseForSell
    ) -> None:
        super().__init__(user)
        self.enlist_details = enlist_details

        if not self.is_user_verified(user_details=self.user):
            raise BaseHorseSellingServiceValidator.http_exception(
                message="User otp is not verified"
            )


class GetHorseSellListingValidator(BaseHorseSellingServiceValidator):
    def __init__(self, user: user_dependency, own_listing: bool = False) -> None:
        super().__init__(user)
        self.own_listing = own_listing


class UploadSellImageValidator(BaseHorseSellingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        horse_selling_service_id: str,
        files: List[UploadFile],
    ) -> None:
        super().__init__(user)
        self.horse_selling_service_id = horse_selling_service_id
        self.files = files
        self.service_details = get_selling_service_details_by_service_id(
            service_id=horse_selling_service_id
        )

        if not self.service_created_by_user(
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseSellingServiceValidator.http_exception(
                message="selling service not owned by user"
            )

    @staticmethod
    def service_created_by_user(
        service_details: HorseSellingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id


class UpdateHorseForSellServiceListingValidator(BaseHorseSellingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        horse_selling_service_id: str,
        update_details: UpdateHorseForSellServiceListing,
    ) -> None:
        super().__init__(user)
        self.horse_selling_service_id = horse_selling_service_id
        self.update_details = update_details
        self.service_details = get_selling_service_details_by_service_id(
            service_id=horse_selling_service_id
        )

        if not self.service_created_by_user(
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseSellingServiceValidator.http_exception(
                message="selling service not owned by user"
            )

    @staticmethod
    def service_created_by_user(
        service_details: HorseSellingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id


class CreateSellEnquiryValidator(BaseHorseSellingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        enquiry_details: HorseSellEnquiry,
    ) -> None:
        super().__init__(user)

        self.service_details = get_selling_service_details_by_service_id(
            service_id=enquiry_details.horse_selling_service_id
        )

        if self.service_created_by_user(
            service_details=self.service_details, creator_id=user.id
        ):
            raise BaseHorseSellingServiceValidator.http_exception(
                message="user cannot enquire about own listing"
            )

        self.old_enquiry_details = self.get_enquiry(
            user_id=self.user.id,
            selling_service_id=enquiry_details.horse_selling_service_id,
        )
        self.update_existing = True if self.old_enquiry_details else False

        self.enquiry_details = enquiry_details

    @staticmethod
    def get_enquiry(
        user_id: str, selling_service_id: str
    ) -> Union[HorseSellingServiceEnquiryInternalWithID, None]:
        return get_selling_enquiry_details_by_user_and_selling_service_id(
            user_id=user_id, selling_service_id=selling_service_id
        )

    @staticmethod
    def service_created_by_user(
        service_details: HorseSellingServiceInternalWithID, creator_id: str
    ) -> bool:
        return service_details.provider.provider_id == creator_id


class UpdateSellEnquiryValidator(BaseHorseSellingServiceValidator):
    def __init__(
        self,
        user: user_dependency,
        horse_selling_enquiry_id: str,
        enquiry_details: UpdateHorseSellEnquiry,
    ) -> None:
        super().__init__(user)

        self.horse_sell_enquiry_id = horse_selling_enquiry_id
        self.old_enquiry_details = self.get_enquiry(enquiry_id=horse_selling_enquiry_id)

        self.enquiry_details = enquiry_details

        if not self.enquiry_created_by_user(
            enquiry_details=self.old_enquiry_details, user_id=user.id
        ):
            raise BaseHorseSellingServiceValidator.http_exception(
                message="selected enquiry not created by current user"
            )

    @staticmethod
    def get_enquiry(
        enquiry_id: str,
    ) -> Union[HorseSellingServiceEnquiryInternalWithID, None]:
        return get_selling_enquiry_details_by_enquiry_id(enquiry_id=enquiry_id)

    @staticmethod
    def enquiry_created_by_user(
        enquiry_details: HorseSellingServiceEnquiryInternalWithID, user_id: str
    ) -> bool:
        return enquiry_details.user_id == user_id


class GetHorseSellEnquiryValidator(BaseHorseSellingServiceValidator):
    def __init__(self, user: user_admin_dependency) -> None:
        super().__init__(user)
        self.is_admin = self.user.user_role == UserRoles.ADMIN
