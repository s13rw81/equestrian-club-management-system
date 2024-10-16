from decorators import atomic_transaction
from typing import Optional
from models.reset_password_otp import ResetPasswordOtpInternal
from logging_config import log
from data.db import get_reset_password_otp_collection

reset_password_otp_collection = get_reset_password_otp_collection()


@atomic_transaction
def find_reset_password_otp(session=None, **kwargs) -> Optional[ResetPasswordOtpInternal]:
    log.info(f"inside find_reset_password_otp({kwargs})")

    reset_password_otp = reset_password_otp_collection.find_one(kwargs, session=session)

    if not reset_password_otp:
        log.info(f"No reset_password_otp exists with the provided attributes, returning None")
        return None

    retval = ResetPasswordOtpInternal(**reset_password_otp)

    log.info(f"returning reset_password_otp = {retval}")

    return retval