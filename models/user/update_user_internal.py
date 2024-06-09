from pydantic import BaseModel
from typing import Optional
from models.user.user_internal import EmailVerificationOTP


class UpdateUserInternal(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    hashed_password: Optional[str] = None
    otp_verified: Optional[bool] = None
    email_verification_otp: Optional[EmailVerificationOTP] = None
