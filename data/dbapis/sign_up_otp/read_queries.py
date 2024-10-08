from decorators import atomic_transaction
from typing import Optional
from models.sign_up_otp import SignUpOtpInternal
from logging_config import log
from data.db import get_sign_up_otp_collection

sign_up_otp_collection = get_sign_up_otp_collection()


@atomic_transaction
def find_sign_up_otp(session=None, **kwargs) -> Optional[SignUpOtpInternal]:
    log.info(f"inside find_sign_up_otp({kwargs})")

    sign_up_otp = sign_up_otp_collection.find_one(kwargs, session=session)

    if not sign_up_otp:
        log.info(f"No sign_up_otp exists with the provided attributes, returning None")
        return None

    retval = SignUpOtpInternal(**sign_up_otp)

    log.info(f"returning sign_up_otp = {retval}")

    return retval