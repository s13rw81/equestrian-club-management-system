from ..common_base import CommonBase
from .enums import AvailableService, TimeSlot, WeekDay


class UpdateTrainerInternal(CommonBase):
    # user-fields
    full_name: str = None
    phone_number: str = None
    email_address: str = None
    bio: str = None
    club_affiliation_number: str = None
    available_services: list[AvailableService] = None
    availability: list[WeekDay] = None
    preferred_time_slot: list[TimeSlot] = None
    is_visible: bool = None

    # system-fields
    club_id: str = None
