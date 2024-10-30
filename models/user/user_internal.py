from typing import Optional
from pydantic import field_serializer
from ..common_base import CommonBase
from .enums import (
    EquestrianDiscipline,
    HorseOwnership,
    RidingStage,
    UserRoles, UserCategory, Gender
)


class UserInternal(CommonBase):
    # user-fields
    full_name: str
    email_address: Optional[str] = None
    phone_number: str
    hashed_password: str
    gender: Optional[Gender] = None
    # system fields
    user_role: UserRoles = UserRoles.USER
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None
    user_category: Optional[UserCategory] = None
    image: Optional[str] = None

    @field_serializer(
        "gender",
        "user_role",
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "user_category"
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
