from api.logistics.models import UpdateClubToClubServiceBooking
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

from pymongo.collection import Collection


def save_booking(
    booking: ClubToClubServiceBookingInternal | None,
    collection: Collection,
) -> str:
    """saves the provided booking details for a particular service

    Args:
        booking (ClubToClubServiceBookingInternal | None): booking details
        collection (Collection): collection to save in

    Returns:
        str: booking id of the booking
    """

    log.info(f"save_booking invoked {booking}")
    booking_id = (collection.insert_one(booking.model_dump())).inserted_id

    retval = str(booking_id)

    log.info(f"save_booking() returning booking id {retval}")

    return retval


def save_club_to_club_service_booking_db(
    booking: ClubToClubServiceBookingInternal,
) -> str:
    """saves a club to club service booking in the database

    Args:
        booking (ClubToClubServiceBookingInternal): booking details
    """
    log.info(f"save_club_to_club_service_booking_db() invoked")
    club_to_club_service_booking_collection = booking_collection_mapping.get(
        "club_to_club"
    )
    return save_booking(
        booking=booking, collection=club_to_club_service_booking_collection
    )


def update_club_to_club_service_booking_db(
    booking_id: str,
    booking: UpdateClubToClubServiceBooking,
) -> bool:
    """update the club to club service booking based on booking id

    Args:
        booking_id: str
        booking (UpdateClubToClubServiceBooking)
    """

    log.info(
        f"update_club_to_club_service_booking_db() invoked booking_id {booking_id} booking {booking}"
    )

    filter = {"_id": convert_to_object_id(booking_id)}
    update = {k: v for k, v in booking.model_dump().items() if v != None and k != "_id"}

    collection = booking_collection_mapping.get("club_to_club")

    if not update:
        return False

    update_response = collection.update_one(filter=filter, update={"$set": update})

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
