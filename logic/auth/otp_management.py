from fastapi import status
from fastapi.exceptions import HTTPException
from data.dbapis.user.write_queries import update_user
from data.dbapis.user.read_queries import get_user_by_email
from models.user import UpdateUserInternal, EmailVerificationOTP
from external_services.otp_service import send_otp
from logging_config import log


def send_email_verification_otp_logic(email_address: str) -> bool:
    """
        sends otp in the given email address using
        the corresponding external_service and saves it in the database

        :param email_address: the email_address of the user
        :returns: the result of the database update; a bool
    """

    # TODO: integrate the logic that new OTP won't be generated if the old OTP is less than 10 minutes old

    log.info(f"send_otp_logic invoked: email_address={email_address}")

    user = get_user_by_email(email=email_address)

    sent_otp = send_otp(
        email_address=email_address,
        first_name=user.first_name,
        last_name=user.last_name
    )

    update_user_data = UpdateUserInternal(email_verification_otp=EmailVerificationOTP(otp=sent_otp))

    result = update_user(update_user_data=update_user_data, email_address=email_address)

    return result


def verify_email_verification_otp_logic(email_address: str, user_provided_otp: str) -> bool:
    """
        matches the provided OTP with the database records for
        the corresponding user; if a match is found the database is updated
        accordingly; returns a bool indicating whether a match was found

        :param email_address: the email_address of the user
        :param user_provided_otp: the user provided OTP

        :returns: boolean indicating whether there was a match
    """

    log.info(f"validate_otp invoked: email_address={email_address}, "
                f"user_provided_otp={user_provided_otp}")

    user = get_user_by_email(email=email_address)

    if user.email_verification_otp.otp != user_provided_otp:
        log.info("the OTPs did not match, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid OTP"
        )

    update_user_data = UpdateUserInternal(otp_verified=True)

    result = update_user(update_user_data=update_user_data, email_address=email_address)

    return result
