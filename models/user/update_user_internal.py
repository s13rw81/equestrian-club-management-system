from pydantic import field_serializer
from typing import Optional
from .enums import (
    RidingStage,
    HorseOwnership,
    EquestrianDiscipline,
    UserRoles,
    Gender,
    UserCategory
)
from ..common_base import CommonBase


class UpdateUserInternal(CommonBase):
    # user-fields
    full_name: str = None
    hashed_password: str = None
    gender: Optional[Gender] = None
    # system-fields
    user_role: UserRoles = None
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None
    user_category: Optional[UserCategory] = None
    image: Optional[str] = None
    cover_image: Optional[str] = None

    @field_serializer(
        "gender",
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "user_role",
        "user_category"
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
