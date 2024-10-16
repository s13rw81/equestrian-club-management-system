from ..common_base import CommonBase
from typing import Optional
from datetime import datetime

class ResetPasswordOtpInternal(CommonBase):
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    otp: str
    last_otp_sent_time: datetime
    last_otp_generated_time: datetime
    invalid_verification_attempts: int = 0
    last_invalid_verification_attempt_time: Optional[datetime] = None


