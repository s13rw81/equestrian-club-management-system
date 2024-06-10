from fastapi import status
from typing import Optional
from validators.regex_validators import is_valid_email
from fastapi.exceptions import HTTPException
from data.dbapis.user.write_queries import update_user
from data.dbapis.user.read_queries import get_user_by_email
from models.user import UpdateUserInternal, SignUpVerificationOTP, UserInternal, PasswordResetVerificationOTP
from models.user.enums import SignUpCredentialType
from external_services.otp_service import send_otp_email, send_otp_phone
from logging_config import log


def send_sign_up_otp(user: UserInternal) -> bool:
    """
        sends otp in the sign_up credential of the user using
        the corresponding external_service and saves it in the database

        :param user: the user
        :returns: the result of the database update; a bool
    """

    # TODO: integrate the logic that new OTP won't be generated if the old OTP is less than 10 minutes old

    log.info(f"inside send_sign_up_otp(user={user})")

    sent_otp = (send_otp_email(email_address=user.email_address)
                if user.sign_up_credential_type == SignUpCredentialType.EMAIL_ADDRESS
                else send_otp_phone(phone_number=user.phone_number))

    update_user_data = UpdateUserInternal(sign_up_verification_otp=SignUpVerificationOTP(otp=sent_otp))

    result = update_user(update_user_data=update_user_data, user=user)

    return result


def verify_sign_up_otp(user: UserInternal, user_provided_otp: str) -> bool:
    """
        matches the provided OTP with the database records for
        the corresponding user; if a match is found the database is updated
        accordingly; returns a bool indicating whether a match was found

        :param user: UserInternal
        :param user_provided_otp: the user provided OTP

        :returns: boolean indicating whether there was a match
    """

    log.info(f"verify_sign_up_otp(user={user}, user_provided_otp={user_provided_otp})")

    if not user.sign_up_verification_otp:
        log.info("the user hasn't generated OTP, please generate OTP first")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="please generate OTP first"
        )

    if user.sign_up_verification_otp.otp != user_provided_otp:
        log.info("the OTPs did not match, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid OTP"
        )

    update_user_data = UpdateUserInternal(otp_verified=True)

    result = update_user(update_user_data=update_user_data, user=user)

    return result


def send_reset_password_otp(user: UserInternal) -> bool:
    log.info(f"inside send_reset_password_otp(user={user})")

    sent_otp = (send_otp_email(email_address=user.email_address)
                if user.sign_up_credential_type == SignUpCredentialType.EMAIL_ADDRESS
                else send_otp_phone(phone_number=user.phone_number))

    update_user_data = UpdateUserInternal(password_reset_verification_otp=PasswordResetVerificationOTP(otp=sent_otp))

    result = update_user(update_user_data=update_user_data, user=user)

    return result


def verify_password_reset_otp(user: UserInternal, user_provided_otp: str) -> bool:
    """
        matches the provided OTP with the database records for
        the corresponding user; if a match is found the database is updated
        accordingly; returns a bool indicating whether a match was found

        :param user: UserInternal
        :param user_provided_otp: the user provided OTP

        :returns: boolean indicating whether there was a match
    """

    log.info(f"verify_password_reset_otp(user={user}, user_provided_otp={user_provided_otp})")

    if not user.password_reset_verification_otp:
        log.info("the user hasn't generated password_reset_verification_otp, please generate OTP first")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="please generate password_reset_verification_otp first"
        )

    if user.password_reset_verification_otp.otp != user_provided_otp:
        log.info("the OTPs did not match, raising exception...")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="invalid OTP"
        )

    update_user_data = UpdateUserInternal(otp_verified=True)

    result = update_user(update_user_data=update_user_data, user=user)

    return result
