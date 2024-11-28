from logging_config import log
from fastapi.exceptions import HTTPException
from fastapi import status
import random
from config import (
    OTP_SERVICE_ACTIVATED,
    OTP_SERVICE_API_URL,
    OTP_SERVICE_USERNAME,
    OTP_SERVICE_USER_SENDER,
    OTP_SERVICE_API_KEY
)
import requests

def send_otp_external(otp, phone_number):
    log.info(f"inside send_otp_external(otp={otp}, phone_number={phone_number})")

    request_data = {
      "userName": OTP_SERVICE_USERNAME,
      "numbers": phone_number,
      "userSender": OTP_SERVICE_USER_SENDER,
      "apiKey": OTP_SERVICE_API_KEY,
      "msg": f"OTP FOR KHAYYAL: {otp}"
    }

    request_headers = {
        'Content-Type': 'application/json'
    }

    request_url = OTP_SERVICE_API_URL + "/sendsms.php"

    response = requests.post(request_url, json=request_data, headers=request_headers)

    log.info("request to external otp service has been completed; "
             f"status_code={response.status_code}, "
             f"headers={response.headers}, "
             f"data={response.json()}")

    if response.status_code != 200:
        log.info("failed to send otp, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="failed to send otp..."
        )

    log.info("OTP has been successfully sent, returning True...")
    return True


def generate_otp() -> str:
    log.info("inside generate_otp()")
    # generate a random OTP if otp service is activated, otherwise return default OTP 123654
    retval = str(random.randrange(100000, 1000000)) if OTP_SERVICE_ACTIVATED else "123654"

    log.info(f"returning {retval}")
    return retval


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

    if OTP_SERVICE_ACTIVATED:
        log.info("email OTP service has not yet been implemented; raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="email OTP service has not yet been implemented..."
        )

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

    if OTP_SERVICE_ACTIVATED:
        send_otp_external(otp=otp, phone_number=phone_number)

    return otp
