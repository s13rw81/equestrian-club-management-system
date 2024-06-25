from enum import Enum


class ServiceType(Enum):
    CLUB_TO_CLUB = "club_to_club"
    USER_TRANSFER = "user_transfer"
    USER_TRANSFER_WITH_INSURANCE = "user_transfer_with_insurance"


class ServiceAvailability(Enum):
    AVAILABLE = True
    UN_AVAILABLE = False
