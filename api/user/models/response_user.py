from pydantic import BaseModel, field_serializer
from typing import Optional

from api.countries.models.country_model import CreateCountryDTO
from models.user.enums import (
    RidingStage,
    HorseOwnership,
    EquestrianDiscipline,
    UserRoles,
    Gender, UserCategory
)


class ResponseUser(BaseModel):
    id: str
    full_name: str
    email_address: Optional[str] = None
    phone_number: str
    gender: Optional[Gender] = None
    user_role: UserRoles
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None
    user_category: Optional[UserCategory] = None
    image: Optional[str] = None
    country_id: Optional[str] = None
    cover_image: Optional[str] = None
    country: Optional[CreateCountryDTO] = None


    @field_serializer(
        "gender",
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "user_role",
        "user_category",
        "country_id"
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
