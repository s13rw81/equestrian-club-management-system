from typing import Annotated, List

from fastapi import Depends, HTTPException, UploadFile, status
from pydantic_extra_types.coordinate import Latitude, Longitude

from api.logistics.models.logistics_company_trucks import AddTruck, UpdateTruckDetails
from data.dbapis.logistics.logistics_company.read_queries import (
    get_logistics_company_by_user_id,
)
from data.dbapis.truck.read_queries import (
    get_truck_details_by_id_db,
    is_truck_registered,
)
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.LOGISTIC_COMPANY})),
]

consumer_app_user_dependency = Annotated[
    UserInternal, Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER}))
]


class BaseTruckValidator:

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


class AddTruckValidator(BaseTruckValidator):
    def __init__(self, user: user_dependency, add_truck: AddTruck) -> None:
        super().__init__(user)
        self.add_truck = add_truck

        if not self.is_logistics_company_verified(
            logistics_company_details=self.logistics_company_details
        ):
            raise BaseTruckValidator.http_exception(
                "logistics company is not verified by khayyal admin"
            )

        if self.is_truck_already_registered(
            registration_number=self.add_truck.registration_number
        ):
            raise BaseTruckValidator.http_exception(
                f"truck with the registration number {self.add_truck.registration_number} is already registered"
            )

    @staticmethod
    def is_logistics_company_verified(logistics_company_details: bool) -> bool:
        """based on logistics_company_details return if the logistics_company is verified
        Args:
            logistics_company_details (bool)
        """
        return logistics_company_details.get("is_khayyal_verified", False)

    @staticmethod
    def is_truck_already_registered(registration_number: str) -> bool:
        """returns if the registration number is already registered in khayyal"""
        return is_truck_registered(registration_number=registration_number)


class UploadTruckImagesValidator(BaseTruckValidator):
    def __init__(
        self,
        user: user_dependency,
        truck_id: str,
        images: List[UploadFile],
    ) -> None:
        super().__init__(user)
        self.files = images
        self.truck_id = truck_id
        trucks_owned_by_logistics_company = self.logistics_company_details.get("trucks")

        if not self.truck_owned_by_logistics_company(
            self.truck_id, trucks_owned_by_logistics_company
        ):
            raise BaseTruckValidator.http_exception(
                "truck is not owned by users logistics company"
            )


class GetTrucksValidator(BaseTruckValidator):
    def __init__(self, user: user_dependency) -> None:
        super().__init__(user)


class GetTruckValidator(BaseTruckValidator):
    def __init__(self, user: user_dependency, truck_id: str) -> None:
        super().__init__(user)
        self.truck_id = truck_id
        self.trucks_owned_by_logistics_company = self.logistics_company_details.get(
            "trucks"
        )

        if not self.truck_owned_by_logistics_company(
            self.truck_id, self.trucks_owned_by_logistics_company
        ):
            raise BaseTruckValidator.http_exception(
                "truck is not owned by users logistics company"
            )


class UpdateTruckDetailsValidator(BaseTruckValidator):
    def __init__(
        self,
        user: user_dependency,
        truck_id: str,
        update_details: UpdateTruckDetails,
    ) -> None:
        super().__init__(user)
        self.truck_id = truck_id
        self.trucks_owned_by_logistics_company = self.logistics_company_details.get(
            "trucks"
        )
        self.update_details = update_details

        if not self.truck_owned_by_logistics_company(
            self.truck_id, self.trucks_owned_by_logistics_company
        ):
            raise BaseTruckValidator.http_exception(
                "truck is not owned by users logistics company"
            )

        if self.update_details.registration_number:
            if self.is_truck_already_registered(
                self.update_details.registration_number
            ):
                raise BaseTruckValidator.http_exception(
                    f"truck with the registration number {self.update_details.registration_number} is already registered"
                )

    @staticmethod
    def is_truck_already_registered(registration_number: str) -> bool:
        """returns if the registration number is already registered in khayyal"""
        return is_truck_registered(registration_number=registration_number)


class FindNearbyTrucksValidator:
    def __init__(
        self,
        user: consumer_app_user_dependency,
        lat: Latitude,
        long: Longitude,
        radius: float = 10,
    ) -> None:
        self.user = user
        self.lat = lat
        self.long = long
        self.radius = radius
