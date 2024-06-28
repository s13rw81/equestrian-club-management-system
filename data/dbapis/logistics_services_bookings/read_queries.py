from pymongo.collection import Collection

from data.db import convert_to_object_id
from logging_config import log
from utils.logistics_utils import LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING


def get_booking(collection: Collection, booking_id: str, consumer_id: str):
    """based on the collection, booking_id and consumer_id return the booking"""

    log.info(
        f"get_booking() invoked for booking_id {booking_id} consumer_id {consumer_id}"
    )

    filter = {
        "consumer.consumer_id": consumer_id,
        "_id": convert_to_object_id(booking_id),
    }

    return collection.find_one(filter=filter)


def get_all_bookings(consumer_id: str, collection: Collection):
    """return all the bookings for the consumer

    Args:
        collection (Collection)
    """
    log.info(f"get_all_bookings() invoked consumer_id {consumer_id}")
    return collection.find({"consumer.consumer_id": consumer_id})


def get_all_club_to_club_service_bookings_db(consumer_id: str):
    """returns all the club to club service booking for the user

    Returns:
        list of all bookings
    """
    log.info(f"get_all_club_to_club_service_bookings_db() invoked")

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get("club_to_club")
    return get_all_bookings(consumer_id=consumer_id, collection=collection)


def get_club_to_club_service_booking_by_booking_id_db(
    consumer_id: str,
    booking_id: str,
) -> dict:
    """return the club to club service booking for a particular booking id

    Args:
        consumer_id (str)
        booking_id (str)

    """

    log.info(
        f"get_club_to_club_service_booking_by_booking_id_db() invoked consumer_id {consumer_id} booking_id {booking_id}"
    )

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get("club_to_club")

    booking = get_booking(
        collection=collection, booking_id=booking_id, consumer_id=consumer_id
    )

    log.info(f"get_club_to_club_service_booking_by_booking_id_db() returning {booking}")

    return booking


def get_user_transfer_service_booking_by_booking_id(
    consumer_id: str,
    booking_id: str,
) -> dict:
    """return the user transfer service booking for a particular booking id

    Args:
        consumer_id (str)
        booking_id (str)

    """

    log.info(
        f"get_user_transfer_service_booking_by_booking_id() invoked consumer_id {consumer_id} booking_id {booking_id}"
    )

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get("user_transfer")

    booking = get_booking(
        collection=collection, booking_id=booking_id, consumer_id=consumer_id
    )

    log.info(f"get_user_transfer_service_booking_by_booking_id() returning {booking}")

    return booking


def get_all_user_transfer_service_bookings_db(consumer_id: str):
    """returns all the user transfer service booking for the user

    Returns:
        list of all bookings
    """
    log.info(f"get_all_user_transfer_service_bookings_db() invoked")

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get("user_transfer")
    return get_all_bookings(consumer_id=consumer_id, collection=collection)


def get_user_transfer_service_booking_by_booking_id(
    consumer_id: str,
    booking_id: str,
) -> dict:
    """return the user transfer service booking for a particular booking id

    Args:
        consumer_id (str)
        booking_id (str)

    """

    log.info(
        f"get_user_transfer_service_booking_by_booking_id() invoked consumer_id {consumer_id} booking_id {booking_id}"
    )

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get("user_transfer")

    booking = get_booking(
        collection=collection, booking_id=booking_id, consumer_id=consumer_id
    )

    log.info(f"get_user_transfer_service_booking_by_booking_id() returning {booking}")

    return booking
