from enum import Enum

from data.db import get_collection


class LogisticsService(Enum):
    CLUB_TO_CLUB = "club_to_club"
    USER_TRANSFER = "user_transfer"
    LUGGAGE_TRANSFER = "luggage_transfer"


LOGISTICS_SERVICE_COLLECTION_MAPPING = {
    "club_to_club": get_collection("logistics_service_club_to_club"),
    "user_transfer": get_collection("logistics_service_user_transfer"),
    "luggage_transfer": get_collection("logistics_service_luggage_transfer"),
}

LOGISTICS_SERVICE_BOOKINGS_COLLECTION_MAPPING = {
    "club_to_club": get_collection(
        collection_name="logistics_service_club_to_club_booking"
    ),
    "user_transfer": get_collection(
        collection_name="logistics_service_user_transfer_booking"
    ),
    "luggage_transfer": get_collection("logistics_service_luggage_transfer_booking"),
}
