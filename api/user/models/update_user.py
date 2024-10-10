from pydantic import BaseModel
from typing import Optional
from models.user import RidingStage, HorseOwnership, EquestrianDiscipline


class UpdateUser(BaseModel):
    full_name: Optional[str] = None
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None


