from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from data.dbapis.logistics_company_services.read_queries import (
    get_all_club_to_club_services,
    get_all_luggage_transfer_services,
    get_all_user_transfer_services,
)
from data.dbapis.logistics_services_bookings.read_queries import (
    get_all_club_to_club_service_bookings_db,
    get_all_luggage_transfer_service_bookings_db,
    get_all_user_transfer_service_bookings_db,
    get_club_to_club_service_booking_by_booking_id_db,
    get_luggage_transfer_service_by_booking_id,
    get_user_transfer_service_booking_by_booking_id,
)
from data.dbapis.logistics_services_bookings.write_queries import (
    save_club_to_club_service_booking_db,
    save_luggage_transfer_service_booking_db,
    save_user_transfer_service_booking_db,
    update_club_to_club_service_booking_db,
    update_luggage_transfer_service_booking_db,
    update_user_transfer_service_booking_db,
)
from data.dbapis.truck.write_queries import update_truck_availability
from logging_config import log
from logic.logistics.service_bookings_truck_availability_check import (
    truck_available_for_service_booking,
)
from models.logistics_service_bookings import (
    ClubToClubServiceBookingInternal,
    Consumer,
    LuggageTransferServiceBookingInternal,
    UserTransferServiceBookingInternal,
)
from models.logistics_service_bookings.enums import BookingStatus
from models.truck.enums import TruckAvailability
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl
from utils.logistics_utils import LogisticsService

from .models import (
    BookClubToClubService,
    BookLuggageTransferService,
    BookUserTransferService,
    ClubToClubServiceBooking,
    ClubToClubServices,
    LuggageTransferService,
    LuggageTransferServiceBooking,
    ResponseBookClubToClubServiceBooking,
    ResponseBookLuggageTransferService,
    ResponseBookUserTransferService,
    ResponseClubToClubServiceBooking,
    ResponseClubToClubServices,
    ResponseLuggageTransferService,
    ResponseLuggageTransferServiceBooking,
    ResponseUserTransferServiceBooking,
    ResponseUserTransferServices,
    UpdateClubToClubServiceBooking,
    UpdateLuggageTransferServiceBooking,
    UpdateUserTransferServiceBooking,
    UserTransferServiceBooking,
    UserTransferServices,
)

service_booking_router = APIRouter(prefix="/services", tags=["logistics-user"])


@service_booking_router.get(
    "/get-club-to-club-services", response_model=List[ResponseClubToClubServices]
)
def get_club_to_club_services(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.LOGISTIC_COMPANY,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(f"{request.url.path} invoked")

    club_to_club_services = get_all_club_to_club_services()
    response = [ClubToClubServices(**service) for service in club_to_club_services]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.post("/book-club-to-club-service/{service_id}")
def book_club_to_club_services(
    service_id: str,
    booking_details: BookClubToClubService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
) -> ResponseBookClubToClubServiceBooking:
    log.info(f"{request.url.path} invoked booking_details {booking_details}")

    truck_availability = truck_available_for_service_booking(
        service_id=service_id,
        service_type=LogisticsService.CLUB_TO_CLUB.value,
        logistics_company_id=booking_details.logistics_company_id,
        truck_id=booking_details.truck_id,
    )
    if not truck_availability.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=truck_availability.message
        )

    booking_status = BookingStatus.CREATED

    booking = ClubToClubServiceBookingInternal(
        consumer=Consumer(consumer_id=user.id, consumer_type=user.user_role),
        horse_id=booking_details.horse_id,
        source_club_id=booking_details.source_club_id,
        destination_club_id=booking_details.destination_club_id,
        logistics_company_id=booking_details.logistics_company_id,
        source_location=booking_details.source_location,
        destination_location=booking_details.destination_location,
        current_location=booking_details.current_location,
        truck_id=booking_details.truck_id,
        pickup_time=booking_details.pickup_time,
        booking_status=booking_status,
        service_id=service_id,
    )

    booking_id = save_club_to_club_service_booking_db(booking=booking)

    truck_availability_updated = update_truck_availability(
        truck_id=booking_details.truck_id,
        availability=TruckAvailability.UN_AVAILABLE.value,
    )

    if not booking_id or not truck_availability_updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    response = ResponseBookClubToClubServiceBooking(
        booking_id=booking_id,
        booking_status=booking_status,
        message="booking created Successfully.",
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@service_booking_router.put("/update-club-to-club-service-booking/{booking_id}")
def update_club_to_club_booking(
    booking_id: str,
    booking_update_details: UpdateClubToClubServiceBooking,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(
        f"{request.url.path} invoked booking_update_details {booking_update_details}"
    )

    if (
        booking_update_details.booking_status
        and booking_update_details.booking_status != BookingStatus.CANCELLED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user can only cancel the booking",
        )

    booking_details = get_club_to_club_service_booking_by_booking_id_db(
        consumer_id=user.id, booking_id=booking_id
    )

    if not booking_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    booking = ClubToClubServiceBookingInternal(**booking_details)

    if booking.booking_status != BookingStatus.CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"cannot update this booking as booking status is {booking.booking_status.value}",
        )

    updated = update_club_to_club_service_booking_db(
        booking_id=booking_id, booking=booking_update_details
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cannot update the booking",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@service_booking_router.get(
    "/get-club-to-club-service-bookings",
    response_model=List[ResponseClubToClubServiceBooking],
)
def get_club_to_club_service_bookings(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    club_to_club_bookings = get_all_club_to_club_service_bookings_db(
        consumer_id=user.id
    )
    response = [
        ClubToClubServiceBooking(**booking) for booking in club_to_club_bookings
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.get(
    "/get-club-to-club-service-booking/{booking_id}",
    response_model=ResponseClubToClubServiceBooking,
)
def get_club_to_club_service_booking(
    booking_id: str,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    booking = get_club_to_club_service_booking_by_booking_id_db(
        consumer_id=user.id, booking_id=booking_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    club_to_club_booking = ClubToClubServiceBooking(**booking)

    log.info(f"{request.url.path} returning {club_to_club_booking}")

    return club_to_club_booking


@service_booking_router.get(
    "/get-user-transfer-services", response_model=List[ResponseUserTransferServices]
)
def get_user_transfer_services(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(f"{request.url.path} invoked")

    user_transfer_services = get_all_user_transfer_services()
    response = [UserTransferServices(**service) for service in user_transfer_services]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.post("/book-user-transfer-service/{service_id}")
def book_user_transfer_service(
    service_id: str,
    booking_details: BookUserTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
) -> ResponseBookUserTransferService:
    log.info(f"{request.url.path} invoked booking_details {booking_details}")

    truck_availability = truck_available_for_service_booking(
        service_id=service_id,
        service_type=LogisticsService.USER_TRANSFER.value,
        logistics_company_id=booking_details.logistics_company_id,
        truck_id=booking_details.truck_id,
    )
    if not truck_availability.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=truck_availability.message
        )

    booking_status = BookingStatus.CREATED

    booking = UserTransferServiceBookingInternal(
        consumer=Consumer(consumer_id=user.id, consumer_type=user.user_role),
        service_id=service_id,
        logistics_company_id=booking_details.logistics_company_id,
        truck_id=booking_details.truck_id,
        source_location=booking_details.source_location,
        destination_location=booking_details.destination_location,
        current_location=booking_details.source_location,
        pickup_time=booking_details.pickup_time,
        booking_status=booking_status,
        horse_info=booking_details.horse_info,
        groomer_info=booking_details.groomer_info,
    )

    booking_id = save_user_transfer_service_booking_db(booking=booking)

    truck_availability_updated = update_truck_availability(
        truck_id=booking_details.truck_id,
        availability=TruckAvailability.UN_AVAILABLE.value,
    )

    if not booking_id or not truck_availability_updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    response = ResponseBookUserTransferService(
        booking_id=booking_id,
        booking_status=booking_status,
        message="booking created Successfully.",
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@service_booking_router.put("/update-user-transfer-service-booking/{booking_id}")
def update_user_transfer_service_booking(
    booking_id: str,
    booking_update_details: UpdateUserTransferServiceBooking,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(
        f"{request.url.path} invoked booking_update_details {booking_update_details}"
    )

    if (
        booking_update_details.booking_status
        and booking_update_details.booking_status != BookingStatus.CANCELLED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user can only cancel the booking",
        )

    booking_details = get_user_transfer_service_booking_by_booking_id(
        consumer_id=user.id, booking_id=booking_id
    )
    if not booking_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    booking = UserTransferServiceBookingInternal(**booking_details)

    if booking.booking_status != BookingStatus.CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"cannot update this booking as booking status is {booking.booking_status.value}",
        )

    updated = update_user_transfer_service_booking_db(
        booking_id=booking_id, booking=booking_update_details
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cannot update the booking",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@service_booking_router.get(
    "/get-user-transfer-service-bookings",
    response_model=List[ResponseUserTransferServiceBooking],
)
def get_user_transfer_service_bookings(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    user_transfer_bookings = get_all_user_transfer_service_bookings_db(
        consumer_id=user.id
    )
    response = [
        UserTransferServiceBooking(**booking) for booking in user_transfer_bookings
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.get(
    "/get-user-transfer-service-booking/{booking_id}",
    response_model=ResponseUserTransferServiceBooking,
)
def get_user_transfer_service_booking(
    booking_id: str,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    booking = get_user_transfer_service_booking_by_booking_id(
        consumer_id=user.id, booking_id=booking_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    user_transfer_booking = UserTransferServiceBooking(**booking)

    log.info(f"{request.url.path} returning {user_transfer_booking}")

    return user_transfer_booking


@service_booking_router.get(
    "/get-luggage-transfer-services",
    response_model=List[ResponseLuggageTransferService],
)
def get_luggage_transfer_services(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(f"{request.url.path} invoked")

    luggage_transfer_services = get_all_luggage_transfer_services()
    response = [
        LuggageTransferService(**service) for service in luggage_transfer_services
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.post("/book-luggage-transfer-service/{service_id}")
def book_luggage_transfer_service(
    service_id: str,
    booking_details: BookLuggageTransferService,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
) -> ResponseBookLuggageTransferService:
    log.info(f"{request.url.path} invoked booking_details {booking_details}")

    truck_availability = truck_available_for_service_booking(
        service_id=service_id,
        service_type=LogisticsService.LUGGAGE_TRANSFER.value,
        logistics_company_id=booking_details.logistics_company_id,
        truck_id=booking_details.truck_id,
    )
    if not truck_availability.is_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=truck_availability.message
        )

    booking_status = BookingStatus.CREATED

    booking = LuggageTransferServiceBookingInternal(
        consumer=Consumer(consumer_id=user.id, consumer_type=user.user_role),
        service_id=service_id,
        logistics_company_id=booking_details.logistics_company_id,
        truck_id=booking_details.truck_id,
        source_location=booking_details.source_location,
        destination_location=booking_details.destination_location,
        current_location=booking_details.current_location,
        pickup_time=booking_details.pickup_time,
        booking_status=booking_status,
        items_to_move=booking_details.items_to_move,
        dedicated_labour=booking_details.dedicated_labour,
    )

    booking_id = save_luggage_transfer_service_booking_db(booking=booking)

    truck_availability_updated = update_truck_availability(
        truck_id=booking_details.truck_id,
        availability=TruckAvailability.UN_AVAILABLE.value,
    )

    if not booking_id or not truck_availability_updated:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the transfer in the database",
        )

    response = ResponseBookLuggageTransferService(
        booking_id=booking_id,
        booking_status=booking_status,
        message="booking created Successfully.",
    )

    log.info(f"{request.url.path} returning : {response}")

    return response


@service_booking_router.put("/update-luggage-transfer-service-booking/{booking_id}")
def update_luggage_transfer_service_booking(
    booking_id: str,
    booking_update_details: UpdateLuggageTransferServiceBooking,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):
    log.info(
        f"{request.url.path} invoked booking_update_details {booking_update_details}"
    )

    if (
        booking_update_details.booking_status
        and booking_update_details.booking_status != BookingStatus.CANCELLED
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user can only cancel the booking",
        )

    booking_details = get_luggage_transfer_service_by_booking_id(
        consumer_id=user.id, booking_id=booking_id
    )

    if not booking_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    booking = LuggageTransferServiceBookingInternal(**booking_details)

    if booking.booking_status != BookingStatus.CREATED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"cannot update this booking as booking status is {booking.booking_status.value}",
        )

    updated = update_luggage_transfer_service_booking_db(
        booking_id=booking_id, booking=booking_update_details
    )

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="cannot update the booking",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@service_booking_router.get(
    "/get-luggage-transfer-service-bookings",
    response_model=List[ResponseLuggageTransferServiceBooking],
)
def get_luggage_transfer_service_bookings(
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    luggage_transfer_bookings = get_all_luggage_transfer_service_bookings_db(
        consumer_id=user.id
    )
    response = [
        LuggageTransferServiceBooking(**booking)
        for booking in luggage_transfer_bookings
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@service_booking_router.get(
    "/get-luggage-transfer-service-booking/{booking_id}",
    response_model=ResponseLuggageTransferServiceBooking,
)
def get_luggage_transfer_service_booking(
    booking_id: str,
    request: Request,
    user: Annotated[
        UserInternal,
        Depends(
            RoleBasedAccessControl(
                allowed_roles={
                    UserRoles.ADMIN,
                    UserRoles.USER,
                }
            )
        ),
    ],
):

    log.info(f"{request.url.path} invoked")

    booking = get_luggage_transfer_service_by_booking_id(
        consumer_id=user.id, booking_id=booking_id
    )
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid booking id received",
        )

    luggage_transfer_booking = LuggageTransferServiceBooking(**booking)

    log.info(f"{request.url.path} returning {luggage_transfer_booking}")

    return luggage_transfer_booking
