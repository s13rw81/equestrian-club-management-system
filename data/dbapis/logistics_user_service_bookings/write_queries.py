from api.logistics.models.logistics_user_service_bookings import UpdateBooking
from data.db import convert_to_object_id, get_logistic_service_booking_collection
from logging_config import log
from models.logistics_user_service_bookings.logistics_user_service_bookings import (
    LogisticsServiceBookingInternal,
)

logistic_service_booking_collection = get_logistic_service_booking_collection()


def save_booking(booking: LogisticsServiceBookingInternal) -> str:
    """saves a users booking

    Args:
        booking (LogisticsServiceBookingInternal)

    Returns:
        str: booking id
    """

    log.info(f"save_booking() invoked {booking}")

    booking_id = (
        logistic_service_booking_collection.insert_one(booking.model_dump())
    ).inserted_id
    retval = str(booking_id) if booking_id else None

    log.info(f"save_booking() returning {retval}")

    return retval


def update_service_booking(update_details: UpdateBooking, booking_id: str) -> bool:
    """updates the booking details of the provided booking_id

    Args:
        update_details (UpdateBooking) : details to update
        booking_id (str)

    Returns:
        bool
    """

    log.info(f"update_service_booking() invoked {update_details}")

    filter = {"_id": convert_to_object_id(booking_id)}
    update = {"$set": update_details.model_dump(exclude_none=True)}

    result = logistic_service_booking_collection.update_one(
        filter=filter, update=update
    )

    return result.matched_count == result.modified_count
