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


def get_logistic_service_bookings_by_user(consumer_id: str, fields: List[str] = None):
    """return service bookings made by a particular user

    Args:
        consumer_id (str): id of the user

    Returns:
        Cursor
    """

    log.info(
        f"get_logistic_service_bookings_by_user() invoked consumer_id {consumer_id}"
    )

    filter = {"consumer.consumer_id": consumer_id}

    bookings = logistic_service_booking_collection.find(
        filter=filter, **({"projection": fields} if fields else {})
    )

    return bookings


def get_logistic_service_bookings_by_logistic_company(
    logistic_company_id: str, fields: List[str] = None
):
    """return service bookings made by a particular user

    Args:
        logistic_company_id (str): id of the user

    Returns:
        Cursor
    """

    log.info(
        f"get_logistic_service_bookings_by_logistic_company() invoked logistic_company_id {logistic_company_id}"
    )

    filter = {"logistics_company_id": logistic_company_id}

    bookings = logistic_service_booking_collection.find(
        filter=filter, **({"projection": fields} if fields else {})
    )

    return bookings
