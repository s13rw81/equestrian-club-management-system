from typing import Annotated, List

from fastapi import Depends, HTTPException, UploadFile, status

from api.logistics.models.logistics_company_services import (
    AddClubToClubService,
    UpdateClubToClubService,
)
from data.dbapis.logistics.logistics_company.read_queries import (
    get_logistics_company_by_user_id,
)
from data.dbapis.logistics_company_services.read_queries import (
    club_to_club_service_by_logistics_company_id,
)
from models.logistics_company_services.logistics_company_services import (
    ClubToClubServiceInternalWithID,
)
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.LOGISTIC_COMPANY})),
]


class BaseLogisticsServiceValidator:
    http_exception = lambda message: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )

    def __init__(self, user: user_dependency) -> None:
        self.user = user
        self.logistics_company_details = get_logistics_company_by_user_id(
            user_id=user.id
        )
        self.logistics_company_id = str(self.logistics_company_details.get("_id"))

    @staticmethod
    def truck_owned_by_logistics_company(truck_id: str, trucks_list: List[str]) -> bool:
        """return if the truck_id is present in the trucks_list

        Args:
            truck_id (str)
            trucks_list (List[str]): list of truck ids owned by logistics company

        Returns:
            bool
        """
        return truck_id in trucks_list


class AddClubToClubServiceValidator(BaseLogisticsServiceValidator):
    def __init__(
        self, user: user_dependency, service_details: AddClubToClubService
    ) -> None:
        super().__init__(user)
        self.service_details = service_details
        trucks_owned_by_logistics_company = self.logistics_company_details.get("trucks")

        if self.service_exists(logistics_company_id=self.logistics_company_id):
            raise BaseLogisticsServiceValidator.http_exception(
                message="club to club service already exists for this logistics company"
            )

        for truck_id in self.service_details.trucks:
            if not self.truck_owned_by_logistics_company(
                truck_id=truck_id, trucks_list=trucks_owned_by_logistics_company
            ):
                raise BaseLogisticsServiceValidator.http_exception(
                    message="all trucks must be owned by logistics company"
                )

    @staticmethod
    def service_exists(logistics_company_id: str) -> bool:
        """returns whether the club to club service already exists for the users logistics company"""
        service_details = club_to_club_service_by_logistics_company_id(
            logistics_company_id=logistics_company_id
        )
        return service_details


class GetClubToClubServiceValidator(BaseLogisticsServiceValidator):
    def __init__(self, user: user_dependency) -> None:
        super().__init__(user)


class UpdateClubToClubServiceValidator(BaseLogisticsServiceValidator):
    def __init__(
        self, user: user_dependency, update_details: UpdateClubToClubService
    ) -> None:
        super().__init__(user)
        self.update_details = update_details
        trucks_owned_by_logistics_company = self.logistics_company_details.get("trucks")

        if self.update_details.trucks:
            for truck_id in self.update_details.trucks:
                if not self.truck_owned_by_logistics_company(
                    truck_id=truck_id, trucks_list=trucks_owned_by_logistics_company
                ):
                    raise BaseLogisticsServiceValidator.http_exception(
                        message="all trucks must be owned by logistics company"
                    )


class UploadClubToClubServiceImagesValidator(BaseLogisticsServiceValidator):
    def __init__(self, user: user_dependency, files: List[UploadFile]) -> None:
        super().__init__(user)
        self.files = files
        self.service_details = self.service_exists(
            logistics_company_id=self.logistics_company_id
        )
        self.service_id = self.service_details.service_id

        if not self.service_id:
            raise BaseLogisticsServiceValidator.http_exception(
                message="club to club service does not exists for this logistics company user"
            )

    @staticmethod
    def service_exists(logistics_company_id: str) -> ClubToClubServiceInternalWithID:
        """returns whether the club to club service already exists for the users logistics company"""
        service_details = club_to_club_service_by_logistics_company_id(
            logistics_company_id=logistics_company_id
        )
        return service_details
