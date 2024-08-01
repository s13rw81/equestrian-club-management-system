from typing import List

from data.db import convert_to_object_id, get_logistic_service_booking_collection
from logging_config import log
from models.logistics_user_service_bookings.logistics_user_service_bookings import (
    LogisticsServiceBookingInternal,
)

logistic_service_booking_collection = get_logistic_service_booking_collection()


def get_logistic_service_booking_by_id_db(
    booking_id: str, fields: List[str] = None
) -> LogisticsServiceBookingInternal:
    """return booking details based on booking id

    Args:
        booking_id (str)

    Returns:
        LogisticsServiceBookingInternal
    """

    log.info(f"get_logistic_service_booking_by_id_db() called booking_id {booking_id}")

    filter = {"_id": convert_to_object_id(booking_id)}
    booking_details = logistic_service_booking_collection.find_one(
        filter=filter, **({"projection": fields} if fields else {})
    )

    if booking_details:
        return LogisticsServiceBookingInternal(**booking_details)

    return booking_details
