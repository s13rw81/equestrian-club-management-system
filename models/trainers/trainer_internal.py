from ..common_base import CommonBase
from .enums import AvailableService, WeekDay, TimeSlot
from pydantic import field_serializer




class TrainerInternal(CommonBase):
    # user-fields
    full_name: str
    phone_number: str
    email_address: str
    bio: str
    club_affiliation_number: str
    available_services: list[AvailableService]
    availability: list[WeekDay]
    preferred_time_slot: TimeSlot
    is_visible: bool = True

    # system-fields
    # the id of the user that manages this Trainer entity
    user_id: str
    # the id of the club the trainer is affiliated with
    club_id: str

    @field_serializer(
        "preferred_time_slot"
    )
    def enum_serializer(self, enum):
        if not enum:
            return enum

        return enum.value

    @field_serializer(
        "available_services",
        "availability"
    )
    def enum_serializer_list(self, enum_list):
        if not enum_list:
            return enum_list

        return [enum.value for enum in enum_list]