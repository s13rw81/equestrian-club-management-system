from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime
from utils.date_time import get_current_utc_datetime
from .enums import EquestrianDiscipline, HorseOwnership, RidingStage


class EmailVerificationOTP(BaseModel):
    otp: str
    generated_on: datetime = get_current_utc_datetime()


class UserInternal(BaseModel):
    full_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    hashed_password: str
    otp_verified: bool = False
    email_verification_otp: Optional[EmailVerificationOTP] = None
    riding_stage: RidingStage
    horse_ownership_status: HorseOwnership
    equestrian_discipline: EquestrianDiscipline

    @field_serializer("riding_stage", "horse_ownership_status", "equestrian_discipline")
    def enum_serializer(self, enum):
        return enum.value
