from bson import ObjectId
from pydantic import BaseModel, field_serializer, model_validator, Field
from typing import Optional, Any
from typing_extensions import Self
from datetime import datetime
from utils.date_time import get_current_utc_datetime
from .enums import EquestrianDiscipline, HorseOwnership, RidingStage, SignUpCredentialType, UserRoles


class SignUpVerificationOTP(BaseModel):
    otp: str
    generated_on: datetime = get_current_utc_datetime()


class PasswordResetVerificationOTP(BaseModel):
    otp: str
    generated_on: datetime = get_current_utc_datetime()


class StrObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: Any, x) -> str:
        return str(ObjectId(v))


class UserInternal(BaseModel):
    id: Optional[str] = Field(default_factory = lambda: str(ObjectId()), alias = "_id")
    full_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    hashed_password: str
    otp_verified: bool = False
    sign_up_verification_otp: Optional[SignUpVerificationOTP] = None
    password_reset_verification_otp: Optional[PasswordResetVerificationOTP] = None
    sign_up_credential_type: Optional[SignUpCredentialType] = None
    user_role: UserRoles = UserRoles.USER
    riding_stage: RidingStage
    horse_ownership_status: HorseOwnership
    equestrian_discipline: EquestrianDiscipline

    # def dict(self, *args, **kwargs):
    #     model_dict = super().dict(*args, **kwargs)
    #     model_dict['id'] = str(model_dict['_id'])
    #     return model_dict

    # class Config:
    #     populate_by_name = True
    #     json_encoders = {ObjectId: str}
    #     arbitrary_types_allowed = True

    @field_serializer(
        "user_role",
        "riding_stage",
        "horse_ownership_status",
        "equestrian_discipline",
        "sign_up_credential_type"
    )
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value

    @model_validator(mode = "after")
    def populate_signup_credential_type_if_not_exists(self) -> Self:
        if self.sign_up_credential_type:
            return self

        if self.email_address:
            self.sign_up_credential_type = SignUpCredentialType.EMAIL_ADDRESS
            return self

        self.sign_up_credential_type = SignUpCredentialType.PHONE_NUMBER
        return self
