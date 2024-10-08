from logging_config import log
from fastapi.exceptions import HTTPException
from fastapi import status
import random


def generate_otp() -> str:
    # TODO: Remove it, this is only a temporary fix
    return "123654"
    # return str(random.randrange(100000, 1000000))


def send_otp_email(email_address: str, existing_otp: str = None) -> str:
    """
        sends a randomly generated 6 digit OTP to
        the given email_address and returns the OTP back

        :param email_address: str
        :param existing_otp: str
        :returns: the generated OTP
    """
    log.info(f"inside send_otp_email(email_address={email_address})")
    otp = generate_otp() if not existing_otp else existing_otp
    log.debug(f"GENERATED_OTP={otp}")

    # result = send_dynamic_email(
    #     to_email_address=email_address,
    #     first_name=first_name,
    #     last_name=last_name,
    #     otp=otp
    # )
    #
    # if not result:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="could not send otp email"
    #     )

    return otp


def send_otp_phone(phone_number: str, existing_otp: str = None) -> str:
    """
        sends a randomly generated 6 digit OTP to
        the given email_address and returns the OTP back

        :param phone_number: str
        :param existing_otp: str
        :returns: the generated OTP
    """
    log.info(f"inside send_otp_phone(phone_no={phone_number})")
    otp = generate_otp() if not existing_otp else existing_otp
    log.debug(f"GENERATED_OTP={otp}")

    # result = send_dynamic_email(
    #     to_email_address=email_address,
    #     first_name=first_name,
    #     last_name=last_name,
    #     otp=otp
    # )
    #
    # if not result:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="could not send otp email"
    #     )

    return otp
