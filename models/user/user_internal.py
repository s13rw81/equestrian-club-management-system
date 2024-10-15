from typing import Optional
from pydantic import field_serializer
from ..common_base import CommonBase
from .enums import (
    EquestrianDiscipline,
    HorseOwnership,
    RidingStage,
    UserRoles,
)



class UserInternal(CommonBase):
    full_name: str
    email_address: Optional[str] = None
    phone_number: str
    hashed_password: str
    user_role: UserRoles = UserRoles.USER
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None


    @field_serializer(
        "user_role",
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "sign_up_credential_type",
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
