from ..common_base import CommonBase
from datetime import datetime
from typing import Optional

class UpdateSignUpOtpInternal(CommonBase):
    otp: Optional[str] = None
    last_otp_sent_time: Optional[datetime] = None
    last_otp_generated_time: Optional[datetime] = None
    invalid_verification_attempts: Optional[int] = None
    last_invalid_verification_attempt_time: Optional[datetime] = None
