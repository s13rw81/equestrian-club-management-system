from pymongo.collection import Collection

from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.logistics_service_bookings import ClubToClubServiceBookingInternal

booking_collection_mapping = {
    "club_to_club": get_collection(
        collection_name="logistics_service_club_to_club_booking"
    ),
    "user_transfer": get_collection(
        collection_name="logistics_service_user_transfer_booking"
    ),
    "luggage_transfer": get_collection("logistics_service_luggage_transfer_booking"),
}


def get_booking(collection: Collection, booking_id: str):
    """based on the collection and booking_id return the booking"""
    log.info(f"get_booking() invoked for booking_id {booking_id}")
    filter = {"_id": convert_to_object_id(booking_id)}
    return collection.find_one(filter=filter)


def get_club_to_club_service_booking_by_id(
    booking_id: str,
) -> ClubToClubServiceBookingInternal:
    """return the booking of club to club service based on booking id

    Args:
        booking_id (str)
    Returns:
        ClubToClubServiceBookingInternal
    """
    log.info(
        f"get_club_to_club_service_booking_by_id() invoked : booking_id {booking_id}"
    )

    collection = booking_collection_mapping.get("club_to_club")
    booking = ClubToClubServiceBookingInternal(
        **get_booking(collection=collection, booking_id=booking_id)
    )

    log.info(f"get_club_to_club_service_booking_by_id() returning : {booking}")
    return booking


def get_all_bookings(consumer_id: str, collection: Collection):
    """return all the bookings for the consumer

    Args:
        collection (Collection)
    """

    return collection.find({"consumer.consumer_id": consumer_id})


def get_all_club_to_club_service_bookings_db(consumer_id: str):
    """returns all the club to club service booking for the user

    Returns:
        list of all bookings
    """
    collection = booking_collection_mapping.get("club_to_club")
    return get_all_bookings(consumer_id=consumer_id, collection=collection)


def get_club_to_club_service_booking_by_booking_id_db(
    consumer_id: str,
    booking_id: str,
) -> ClubToClubServiceBookingInternal:
    """return the club to club service booking for a particular booking id

    Args:
        consumer_id (str)
        booking_id (str)

    Returns:
        ClubToClubServiceBookingInternal
    """

    log.info(
        f"get_club_to_club_service_booking_by_booking_id_db() invoked consumer_id {consumer_id} booking_id {booking_id}"
    )

    collection = booking_collection_mapping.get("club_to_club")
    filter = {
        "consumer.consumer_id": consumer_id,
        "_id": convert_to_object_id(booking_id),
    }

    booking = collection.find_one(filter=filter)

    log.info(f"get_club_to_club_service_booking_by_booking_id_db() returning {booking}")
    return ClubToClubServiceBookingInternal(**booking)
