from pydantic import BaseModel, field_validator
from typing import Optional
from models.user.enums import (
    RidingStage,
    HorseOwnership,
    EquestrianDiscipline,
    Gender
)


class UpdateUser(BaseModel):
    full_name: str = None
    gender: Optional[Gender] = None
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None

    @field_validator("full_name")
    def full_name_capitalize(cls, full_name):
        if not full_name:
            return

        return " ".join([item.capitalize() for item in full_name.split()])
