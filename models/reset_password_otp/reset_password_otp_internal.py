from ..common_base import CommonBase
from pydantic import field_validator
from typing import Optional
from datetime import datetime
import pytz

class ResetPasswordOtpInternal(CommonBase):
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    otp: str
    last_otp_sent_time: datetime
    last_otp_generated_time: datetime
    invalid_verification_attempts: int = 0
    last_invalid_verification_attempt_time: Optional[datetime] = None

    @field_validator(
        "last_otp_sent_time",
        "last_otp_generated_time",
        "last_invalid_verification_attempt_time"
    )
    def add_tzinfo_to_datetime_objects(cls, datetime_object):
        if not datetime_object:
            return datetime_object

        return datetime_object.replace(tzinfo=pytz.utc)


