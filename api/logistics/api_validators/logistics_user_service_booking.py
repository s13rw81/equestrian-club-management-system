from typing import Annotated, List

from bson import ObjectId
from fastapi import Depends, HTTPException, status

from api.logistics.models.logistics_user_service_bookings import (
    CreateBooking,
    UpdateBooking,
)
from data.dbapis.logistics_user_service_bookings.read_queries import (
    get_logistic_service_booking_by_id_db,
)
from data.dbapis.truck.read_queries import get_truck_details_by_id_db
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER})),
]

user_logistic_company_dependency = Annotated[
    UserInternal,
    Depends(
        RoleBasedAccessControl(
            allowed_roles={UserRoles.USER, UserRoles.LOGISTIC_COMPANY}
        )
    ),
]


class BaseLogisticsBookingValidator:
    http_exception = lambda message: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )

    def __init__(self, user: user_dependency) -> None:
        self.user = user

    @staticmethod
    def validate_id(truck_id: str) -> bool:
        return ObjectId.is_valid(truck_id)


class CreateBookingValidator(BaseLogisticsBookingValidator):
    def __init__(self, user: user_dependency, booking_details: CreateBooking) -> None:
        super().__init__(user)
        self.booking_details = booking_details

        valid_truck_id = self.validate_id(truck_id=self.booking_details.truck_id)
        if not valid_truck_id:
            raise BaseLogisticsBookingValidator.http_exception(
                message="provided truck id is not valid"
            )

        self.truck_details = get_truck_details_by_id_db(
            truck_id=self.booking_details.truck_id
        )
        if not self.truck_details:
            raise BaseLogisticsBookingValidator.http_exception(
                message="truck details not found"
            )


class UpdateBookingValidator(BaseLogisticsBookingValidator):
    def __init__(
        self,
        user: user_dependency,
        update_details: UpdateBooking,
        logistics_service_booking_id: str,
    ) -> None:
        super().__init__(user)
        self.booking_id = logistics_service_booking_id
        self.update_details = update_details
        self.truck_details = None

        valid_booking_id = self.validate_id(self.booking_id)
        if not valid_booking_id:
            raise BaseLogisticsBookingValidator.http_exception(
                message="provided booking id is not valid"
            )

        self.booking_details = get_logistic_service_booking_by_id_db(
            booking_id=self.booking_id
        )
        if not self.booking_details:
            raise BaseLogisticsBookingValidator.http_exception(
                message="booking details not found"
            )

        if self.booking_details.consumer.consumer_id != self.user.id:
            raise BaseLogisticsBookingValidator.http_exception(
                message="user cannot modify this booking"
            )

        if self.update_details.truck_id:
            if not self.validate_id(truck_id=self.update_details.truck_id):
                raise BaseLogisticsBookingValidator.http_exception(
                    message="provided truck id is not valid"
                )

            self.truck_details = get_truck_details_by_id_db(
                truck_id=self.update_details.truck_id
            )
            if not self.truck_details:
                raise BaseLogisticsBookingValidator.http_exception(
                    message="truck details not found"
                )

            if (
                self.truck_details["logistics_company_id"]
                != self.booking_details.logistics_company_id
            ):
                raise BaseLogisticsBookingValidator.http_exception(
                    message="cannot modify logistics company"
                )


class GetBookingsValidator(BaseLogisticsBookingValidator):
    def __init__(self, user: user_logistic_company_dependency) -> None:
        super().__init__(user)
