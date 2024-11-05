from ..common_base import CommonBase
from .enums import AvailableService, WeekDay, TimeSlot
from pydantic import BaseModel


class Specialization(BaseModel):
    name: str
    years_of_experience: int


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
    specializations: list[Specialization]

    # system-fields
    # the id of the user that manages this Trainer entity
    user_id: str
    # the id of the club the trainer is affiliated with
    club_id: str
