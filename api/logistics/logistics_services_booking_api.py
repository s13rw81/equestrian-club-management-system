from typing import List

from fastapi import APIRouter, HTTPException, Request, Response, status

from data.dbapis.logistics_company_services.read_queries import (
    get_all_club_to_club_services,
    get_all_user_transfer_services,
)
from data.dbapis.logistics_services_bookings.read_queries import (
    get_all_club_to_club_service_bookings_db,
    get_all_user_transfer_service_bookings_db,
    get_club_to_club_service_booking_by_booking_id_db,
    get_user_transfer_service_booking_by_booking_id,
)
from data.dbapis.logistics_services_bookings.write_queries import (
    save_club_to_club_service_booking_db,
    save_user_transfer_service_booking_db,
    update_club_to_club_service_booking_db,
    update_user_transfer_service_booking_db,
)
from data.dbapis.truck.read_queries import (
    get_truck_details_by_id_db,
    get_trucks_by_service_id,
)
from data.dbapis.truck.write_queries import update_truck_availability
from logging_config import log
from models.logistics_service_bookings import (
    ClubToClubServiceBookingInternal,
    Consumer,
    UserTransferServiceBookingInternal,
)
from models.logistics_service_bookings.enums import BookingStatus
from models.truck.enums import TruckAvailability
from utils.logistics_utils import LogisticsService

from .models import (
    BookClubToClubService,
    BookUserTransferService,
    ClubToClubServiceBooking,
    ClubToClubServices,
    ResponseBookClubToClubServiceBooking,
    ResponseBookUserTransferService,
    ResponseClubToClubServiceBooking,
    ResponseClubToClubServices,
    ResponseUserTransferServiceBooking,
    ResponseUserTransferServices,
    UpdateClubToClubServiceBooking,
    UpdateUserTransferServiceBooking,
    UserTransferServiceBooking,
    UserTransferServices,
)

services_router = APIRouter(prefix="/logistics/services", tags=["logistics-services"])


@services_router.get(
    "/get-club-to-club-services", response_model=List[ResponseClubToClubServices]
)
def get_club_to_club_services(request: Request):
    log.info(f"{request.url.path} invoked")

    club_to_club_services = get_all_club_to_club_services()
    response = [ClubToClubServices(**service) for service in club_to_club_services]

    log.info(f"{request.url.path} returning {response}")

    return response


@services_router.post("/book-club-to-club-service")
def book_club_to_club_services(
    booking_details: BookClubToClubService,
    request: Request,
) -> ResponseBookClubToClubServiceBooking:
    log.info(f"{request.url.path} invoked booking_details {booking_details}")

    truck_available_for_service = get_trucks_by_service_id(
        service_id=booking_details.service_id,
        service_type=LogisticsService.CLUB_TO_CLUB.value,
    )
    if booking_details.truck_id not in truck_available_for_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provided truck is not available for club to club transfer",
        )

    truck_details = get_truck_details_by_id_db(
        truck_id=booking_details.truck_id,
        fields=["logistics_company_id", "availability"],
    )

    truck_available = (
        truck_details.get("availability") == TruckAvailability.AVAILABLE.value
    )
    if not truck_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selected truck is not currently available",
        )

    booking_status = BookingStatus.CREATED

    booking = ClubToClubServiceBookingInternal(
        consumer=Consumer(consumer_id=booking_details.consumer_id),
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
        service_id=booking_details.service_id,
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


@services_router.put("/update-club-to-club-service-booking/{booking_id}")
def update_club_to_club_booking(
    consumer_id: str,
    booking_id: str,
    booking_update_details: UpdateClubToClubServiceBooking,
    request: Request,
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

    booking = ClubToClubServiceBookingInternal(
        **get_club_to_club_service_booking_by_booking_id_db(
            consumer_id=consumer_id, booking_id=booking_id
        )
    )

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


@services_router.get(
    "/get-club-to-club-service-bookings",
    response_model=List[ResponseClubToClubServiceBooking],
)
def get_club_to_club_service_bookings(consumer_id: str, request: Request):

    log.info(f"{request.url.path} invoked")

    club_to_club_bookings = get_all_club_to_club_service_bookings_db(
        consumer_id=consumer_id
    )
    response = [
        ClubToClubServiceBooking(**booking) for booking in club_to_club_bookings
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@services_router.get(
    "/get-club-to-club-service-booking/{booking_id}",
    response_model=ResponseClubToClubServiceBooking,
)
def get_club_to_club_service_booking(
    consumer_id: str, booking_id: str, request: Request
):

    log.info(f"{request.url.path} invoked")

    club_to_club_booking = ClubToClubServiceBooking(
        **get_club_to_club_service_booking_by_booking_id_db(
            consumer_id=consumer_id, booking_id=booking_id
        )
    )

    log.info(f"{request.url.path} returning {club_to_club_booking}")

    return club_to_club_booking


@services_router.get(
    "/get-user-transfer-services", response_model=List[ResponseUserTransferServices]
)
def get_user_transfer_services(request: Request):
    log.info(f"{request.url.path} invoked")

    user_transfer_services = get_all_user_transfer_services()
    response = [UserTransferServices(**service) for service in user_transfer_services]

    log.info(f"{request.url.path} returning {response}")

    return response


@services_router.post("/book-user-transfer-service/{service_id}")
def book_user_transfer_service(
    service_id: str,
    booking_details: BookUserTransferService,
    request: Request,
) -> ResponseBookUserTransferService:
    log.info(f"{request.url.path} invoked booking_details {booking_details}")

    truck_available_for_service = get_trucks_by_service_id(
        service_id=booking_details.service_id,
        service_type=LogisticsService.USER_TRANSFER.value,
    )
    if booking_details.truck_id not in truck_available_for_service:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="provided truck is not available for club to club transfer",
        )

    truck_details = get_truck_details_by_id_db(
        truck_id=booking_details.truck_id,
        fields=["logistics_company_id", "availability"],
    )

    truck_available = (
        truck_details.get("availability") == TruckAvailability.AVAILABLE.value
    )
    if not truck_available:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="selected truck is not currently available",
        )

    booking_status = BookingStatus.CREATED

    booking = UserTransferServiceBookingInternal(
        consumer=Consumer(
            consumer_id=booking_details.consumer_id, consumer_type="USER"
        ),
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


@services_router.put("/update-user-transfer-service-booking/{booking_id}")
def update_user_transfer_service_booking(
    consumer_id: str,
    booking_id: str,
    booking_update_details: UpdateUserTransferServiceBooking,
    request: Request,
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

    booking = UserTransferServiceBookingInternal(
        **get_user_transfer_service_booking_by_booking_id(
            consumer_id=consumer_id, booking_id=booking_id
        )
    )

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


@services_router.get(
    "/get-user-transfer-service-bookings",
    response_model=List[ResponseUserTransferServiceBooking],
)
def get_user_transfer_service_bookings(consumer_id: str, request: Request):

    log.info(f"{request.url.path} invoked")

    club_to_club_bookings = get_all_user_transfer_service_bookings_db(
        consumer_id=consumer_id
    )
    response = [
        UserTransferServiceBooking(**booking) for booking in club_to_club_bookings
    ]

    log.info(f"{request.url.path} returning {response}")

    return response


@services_router.get(
    "/get-user-transfer-service-booking/{booking_id}",
    response_model=ResponseUserTransferServiceBooking,
)
def get_user_transfer_service_booking(
    consumer_id: str,
    booking_id: str,
    request: Request,
):

    log.info(f"{request.url.path} invoked")

    club_to_club_booking = UserTransferServiceBooking(
        **get_user_transfer_service_booking_by_booking_id(
            consumer_id=consumer_id, booking_id=booking_id
        )
    )

    log.info(f"{request.url.path} returning {club_to_club_booking}")

    return club_to_club_booking
