from pydantic import BaseModel, field_serializer
from typing import Optional
from models.user.enums import RidingStage, HorseOwnership, EquestrianDiscipline, UserRoles


class ResponseUser(BaseModel):
    id: str
    full_name: str
    email_address: Optional[str] = None
    phone_number: str
    user_role: UserRoles
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None

    @field_serializer("riding_stage", "horse_ownership_status", "equestrian_discipline", "user_role")
    def enum_serializer(self, enum):
        if not enum:
            return
            
        return enum.value
