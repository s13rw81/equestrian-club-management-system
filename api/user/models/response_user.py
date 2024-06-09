from pydantic import BaseModel, field_serializer
from typing import Optional
from models.user.enums import RidingStage, HorseOwnership, EquestrianDiscipline


class ResponseUser(BaseModel):
    full_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    otp_verified: bool
    riding_stage: RidingStage
    horse_ownership_status: HorseOwnership
    equestrian_discipline: EquestrianDiscipline

    @field_serializer("riding_stage", "horse_ownership_status", "equestrian_discipline")
    def enum_serializer(self, enum):
        return enum.value
