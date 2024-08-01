from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from data.dbapis.logistics_user_service_bookings.write_queries import (
    save_booking,
    update_service_booking,
)
from logging_config import log
from models.logistics_user_service_bookings.logistics_user_service_bookings import (
    Consumer,
    LogisticsServiceBookingInternal,
)

from .api_validators.logistics_user_service_booking import (
    CreateBookingValidator,
    UpdateBookingValidator,
)
from .models.logistics_user_service_bookings import ResponseCreateBooking

user_service_booking_router = APIRouter(tags=["users-logistics"])


@user_service_booking_router.post("/create-booking")
def create_booking(
    request: Request, payload: Annotated[CreateBookingValidator, Depends()]
) -> ResponseCreateBooking:
    log.info(f"{request.url.path} invoked payload {payload}")

    user = payload.user
    booking_details = payload.booking_details
    truck_details = payload.truck_details

    consumer = Consumer(consumer_id=user.id)

    booking = LogisticsServiceBookingInternal(
        logistics_company_id=truck_details["logistics_company_id"],
        truck_id=booking_details.truck_id,
        consumer=consumer,
        pickup=booking_details.pickup,
        destination=booking_details.destination,
        groomer=booking_details.groomer,
        details=booking_details.details,
    )

    booking_id = save_booking(booking=booking)

    if not booking_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to create booking",
        )

    response = ResponseCreateBooking(logistic_service_booking=booking_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@user_service_booking_router.put("/update-booking/{logistics_service_booking_id}")
def update_booking(
    request: Request, payload: Annotated[UpdateBookingValidator, Depends()]
):
    log.info(f"{request.url.path} invoked payload {payload}")

    update_details = payload.update_details
    booking_id = payload.booking_id

    update_service_booking(update_details=update_details, booking_id=booking_id)

    return {"status": "OK"}
