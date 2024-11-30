from pydantic import BaseModel, field_serializer

from models.trainers.enums import AvailableService, TimeSlot, WeekDay


class GetTrainerDTO(BaseModel):
    id: str
    full_name: str
    phone_number: str
    email_address: str
    bio: str
    club_affiliation_number: str
    available_services: list[AvailableService]
    availability: list[WeekDay]
    preferred_time_slot: list[TimeSlot]
    is_visible: bool
    club_id: str
    specializations: list[str]
    years_of_experience: int

    @field_serializer("preferred_time_slot")
    def enum_serializer(self, enum_list):
        if not enum_list:
            return enum_list

        return [enum.value for enum in enum_list]

    @field_serializer("available_services", "availability")
    def enum_serializer_list(self, enum_list):
        if not enum_list:
            return enum_list

        return [enum.value for enum in enum_list]
