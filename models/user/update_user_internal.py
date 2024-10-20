from pydantic import BaseModel, field_serializer
from typing import Optional
from .enums import (
    RidingStage,
    HorseOwnership,
    EquestrianDiscipline,
    UserRoles
)
from ..common_base import CommonBase


class UpdateUserInternal(CommonBase):
    full_name: str = None
    hashed_password: str = None
    user_role: UserRoles = None
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None

    @field_serializer(
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "user_role"
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
