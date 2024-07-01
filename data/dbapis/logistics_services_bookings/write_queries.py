from pymongo.collection import Collection

from api.logistics.models import (
    UpdateClubToClubServiceBooking,
    UpdateLuggageTransferServiceBooking,
    UpdateUserTransferServiceBooking,
)
from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.logistics_service_bookings import (
    ClubToClubServiceBookingInternal,
    LuggageTransferServiceBookingInternal,
    UserTransferServiceBookingInternal,
)
from utils.logistics_utils import (
    LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING,
    LogisticsService,
)


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

    club_to_club_service_booking_collection = (
        LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
            LogisticsService.CLUB_TO_CLUB.value
        )
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

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
        LogisticsService.CLUB_TO_CLUB.value
    )

    if not update:
        return False

    update_response = collection.update_one(filter=filter, update={"$set": update})

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1


def save_user_transfer_service_booking_db(
    booking: UserTransferServiceBookingInternal,
) -> str:
    """saves a user transfer service booking in the database

    Args:
        booking (UserTransferServiceBookingInternal): booking details
    """
    log.info(f"save_user_transfer_service_booking_db() invoked")

    user_transfer_service_booking_collection = (
        LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
            LogisticsService.USER_TRANSFER.value
        )
    )
    return save_booking(
        booking=booking, collection=user_transfer_service_booking_collection
    )


def update_user_transfer_service_booking_db(
    booking_id: str,
    booking: UpdateUserTransferServiceBooking,
) -> bool:
    """update the user transfer service booking based on booking id

    Args:
        booking_id: str
        booking (UpdateUserTransferServiceBooking)
    """

    log.info(
        f"update_user_transfer_service_booking_db() invoked booking_id {booking_id} booking {booking}"
    )

    filter = {"_id": convert_to_object_id(booking_id)}
    update = {k: v for k, v in booking.model_dump().items() if v != None and k != "_id"}

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
        LogisticsService.USER_TRANSFER.value
    )

    if not update:
        return False

    update_response = collection.update_one(filter=filter, update={"$set": update})

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1


def save_luggage_transfer_service_booking_db(
    booking: LuggageTransferServiceBookingInternal,
) -> str:
    """saves a luggage transfer service booking in the database

    Args:
        booking (LuggageTransferServiceBookingInternal): booking details
    """
    log.info(f"save_luggage_transfer_service_booking_db() invoked")

    luggage_transfer_service_booking_collection = (
        LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
            LogisticsService.LUGGAGE_TRANSFER.value
        )
    )
    return save_booking(
        booking=booking, collection=luggage_transfer_service_booking_collection
    )


def update_luggage_transfer_service_booking_db(
    booking_id: str,
    booking: UpdateLuggageTransferServiceBooking,
) -> bool:
    """update the luggage transfer service booking based on booking id

    Args:
        booking_id: str
        booking (UpdateLuggageTransferServiceBooking)
    """

    log.info(
        f"update_luggage_transfer_service_booking_db() invoked booking_id {booking_id} booking {booking}"
    )

    filter = {"_id": convert_to_object_id(booking_id)}
    update = {k: v for k, v in booking.model_dump().items() if v != None and k != "_id"}

    collection = LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING.get(
        LogisticsService.LUGGAGE_TRANSFER.value
    )

    if not update:
        return False

    update_response = collection.update_one(filter=filter, update={"$set": update})

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
