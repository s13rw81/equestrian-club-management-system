from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field, field_serializer, model_validator
from typing_extensions import Self

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime

from .enums import (
    EquestrianDiscipline,
    HorseOwnership,
    RidingStage,
    SignUpCredentialType,
    UserRoles,
)


class SignUpVerificationOTP(BaseModel):
    otp: str
    generated_on: datetime = get_current_utc_datetime()


class PasswordResetVerificationOTP(BaseModel):
    otp: str
    generated_on: datetime = get_current_utc_datetime()


class UserInternal(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    full_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    hashed_password: str
    otp_verified: bool = False
    sign_up_verification_otp: Optional[SignUpVerificationOTP] = None
    password_reset_verification_otp: Optional[PasswordResetVerificationOTP] = None
    sign_up_credential_type: Optional[SignUpCredentialType] = None
    user_role: UserRoles = UserRoles.USER
    riding_stage: Optional[RidingStage] = None
    horse_ownership_status: Optional[HorseOwnership] = None
    equestrian_discipline: Optional[EquestrianDiscipline] = None

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}

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

    @model_validator(mode="after")
    def populate_signup_credential_type_if_not_exists(self) -> Self:
        if self.sign_up_credential_type:
            return self

        if self.email_address:
            self.sign_up_credential_type = SignUpCredentialType.EMAIL_ADDRESS
            return self

        self.sign_up_credential_type = SignUpCredentialType.PHONE_NUMBER
        return self
