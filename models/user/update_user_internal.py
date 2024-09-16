from pydantic import BaseModel, field_serializer
from typing import Optional
from .user_internal import SignUpVerificationOTP, PasswordResetVerificationOTP
from .enums import RidingStage, HorseOwnership, EquestrianDiscipline, UserRoles


class UpdateUserInternal(BaseModel):
    full_name: Optional[str] = None
    hashed_password: Optional[str] = None
    otp_verified: Optional[bool] = None
    sign_up_verification_otp: Optional[SignUpVerificationOTP] = None
    password_reset_verification_otp: Optional[PasswordResetVerificationOTP] = None
    user_role: Optional[UserRoles] = None
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
