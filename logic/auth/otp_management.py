from data.dbapis.user.write_queries import update_user
from data.dbapis.sign_up_otp import save_sign_up_otp, update_sign_up_otp, find_sign_up_otp
from decorators import atomic_transaction
from external_services.otp_service import send_otp_email, send_otp_phone
from fastapi import status
from fastapi.exceptions import HTTPException
from logging_config import log
from logic.auth import generate_password_hash
from models.sign_up_otp import SignUpOtpInternal, UpdateSignUpOtpInternal
from models.user import UpdateUserInternal, UserInternal, PasswordResetVerificationOTP
from models.user.enums import SignUpCredentialType
from datetime import datetime, timedelta
import pytz


def send_sign_up_otp(email_address: str = None, phone_number: str = None) -> bool:
    log.info(f"inside send_sign_up_otp(email_address={email_address}, phone_number={phone_number})")

    if email_address and phone_number:
        log.info("email_address and phone_number cannot be present simultaneously, raising ValueError")
        raise ValueError("email_address and phone_number cannot be present simultaneously")

    if not (email_address or phone_number):
        log.info("either email_address or phone_number must be present, raising ValueError")
        raise ValueError("either email_address or phone_number must be present, raising ValueError")

    sign_up_otp = (find_sign_up_otp(email_address=email_address)
                   if email_address else find_sign_up_otp(phone_number=phone_number))

    existing_otp = None

    if sign_up_otp:
        log.info("sign up otp is already present...")

        two_minutes_ago_time = datetime.now(pytz.utc) - timedelta(minutes=2)

        if sign_up_otp.last_otp_sent_time > two_minutes_ago_time:
            log.info("last otp was generated less than two minutes ago, raising exception...")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="last otp was generated less than two minutes ago, please wait before generating a new otp..."
            )

        five_minutes_ago_time = datetime.now(pytz.utc) - timedelta(minutes=5)
        if sign_up_otp.last_otp_generated_time > five_minutes_ago_time:
            log.info("last otp was generated less than five minutes ago, resending the existing otp...")
            existing_otp = sign_up_otp.otp

    sent_otp = (send_otp_email(email_address=email_address, existing_otp=existing_otp) if email_address
                else send_otp_phone(phone_number=phone_number, existing_otp=existing_otp))

    if sign_up_otp:
        log.info("sign_up_otp already exists... updating the database record...")

        update_sign_up_otp_data = UpdateSignUpOtpInternal(
            last_updated_on=datetime.now(pytz.utc),
            id=sign_up_otp.id,
            otp=sent_otp,
            last_otp_sent_time=datetime.now(pytz.utc),
            last_otp_generated_time=datetime.now(pytz.utc) if not existing_otp else sign_up_otp.last_otp_generated_time
        )

        result = update_sign_up_otp(update_sign_up_otp_data=update_sign_up_otp_data)

        log.info(f"update completed, returned result = {result}")

        return True

    log.info("sign_up_otp does not exist... creating fresh record in the database...")

    sign_up_otp_data = SignUpOtpInternal(
        email_address=email_address,
        phone_number=phone_number,
        otp=sent_otp,
        last_otp_sent_time=datetime.now(pytz.utc),
        last_otp_generated_time=datetime.now(pytz.utc)
    )

    result = save_sign_up_otp(new_sign_up_otp=sign_up_otp_data)

    log.info(f"creation completed, returned result = {result}")
    return True


@atomic_transaction
def verify_sign_up_otp(
        user_provided_otp: str,
        email_address: str = None,
        phone_number: str = None,
        session=None
) -> bool:
    log.info(f"inside verify_signup_otp(user_provided_otp={user_provided_otp}, email_address={email_address}, "
             f"phone_number={phone_number})")

    if email_address and phone_number:
        log.info("email_address and phone_number cannot be present simultaneously, raising ValueError")
        raise ValueError("email_address and phone_number cannot be present simultaneously")

    if not (email_address or phone_number):
        log.info("either email_address or phone_number must be present, raising ValueError")
        raise ValueError("either email_address or phone_number must be present, raising ValueError")

    sign_up_otp = (find_sign_up_otp(email_address=email_address, session=session)
                   if email_address else find_sign_up_otp(phone_number=phone_number, session=session))

    if not sign_up_otp:
        log.info("sign up otp does not exist, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="user has to generate sign up otp before attempting to verify it..."
        )

    five_minutes_ago_time = datetime.now(pytz.utc) - timedelta(minutes=5)

    # if OTP is more than 5 minutes old raise exception
    if sign_up_otp.last_otp_generated_time < five_minutes_ago_time:
        log.info("last OTP was generated more than 5 minutes ago, it has gone stale, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail="OTP has gone stale, please generate new one before attempting to verify..."
        )

    invalid_verification_attempts = sign_up_otp.invalid_verification_attempts

    # if invalid verification attempts is not 0, check for the invalid_verification_attempts invariants
    if sign_up_otp.invalid_verification_attempts:
        log.info(f"invalid_verification_attempts={invalid_verification_attempts}")
        last_invalid_verification_attempt_time = sign_up_otp.last_invalid_verification_attempt_time
        twenty_four_hours_ago_time = datetime.now(pytz.utc) - timedelta(hours=24)

        # if the user has made more than 100 invalid attempts he is blocked from verification attempts
        # for 24 hours
        if ((invalid_verification_attempts > 100) and
                (last_invalid_verification_attempt_time > twenty_four_hours_ago_time)):
            log.info("100 invalid attempts have already been made for the provided credential, and 24 hours have not "
                     "passed yet since the last_invalid_verification_attempt_time, thus raising HTTPException")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="100 invalid attempts have already been made for the provided credential, please try again "
                       "after 24 hours..."
            )

        # if 24 hours has passed by after making 100 invalid verification attempts, reset the counter
        if ((invalid_verification_attempts > 100) and
                (last_invalid_verification_attempt_time < twenty_four_hours_ago_time)):
            log.info("24 hours have already passed since the last_invalid_verification_attempt_time, resetting the "
                     "database record")
            update_sign_up_otp_data = UpdateSignUpOtpInternal(
                last_updated_on=datetime.now(pytz.utc),
                id=sign_up_otp.id,
                invalid_verification_attempts=0,
                last_invalid_verification_attempt_time=None
            )

            result = update_sign_up_otp(
                update_sign_up_otp_data=update_sign_up_otp_data,
                session=session
            )

            log.info(f"update completed, returned result = {result}")

            # refreshing the data after making the update
            sign_up_otp = (find_sign_up_otp(email_address=email_address, session=session)
                           if email_address else find_sign_up_otp(phone_number=phone_number, session=session))


    if sign_up_otp.otp == user_provided_otp:
        log.info("user_provided_otp matches with the database record... returning True")
        return True

    log.info("invalid attempt at verifying OTP, updating the database record...")
    update_sign_up_otp_data = UpdateSignUpOtpInternal(
        last_updated_on=datetime.now(pytz.utc),
        id=sign_up_otp.id,
        invalid_verification_attempts=(sign_up_otp.invalid_verification_attempts + 1),
        last_invalid_verification_attempt_time=datetime.now(pytz.utc)
    )

    result = update_sign_up_otp(
        update_sign_up_otp_data=update_sign_up_otp_data,
        session=session
    )

    log.info(f"update completed, returned result = {result}")

    log.info("returning False...")
    return False


def send_reset_password_otp(user: UserInternal) -> bool:
    log.info(f"inside send_reset_password_otp(user={user})")

    sent_otp = (send_otp_email(email_address=user.email_address)
                if user.sign_up_credential_type == SignUpCredentialType.EMAIL_ADDRESS
                else send_otp_phone(phone_number=user.phone_number))

    update_user_data = UpdateUserInternal(
        password_reset_verification_otp=PasswordResetVerificationOTP(otp=sent_otp))

    result = update_user(update_user_data=update_user_data, user=user)

    return result


def verify_password_reset_otp(user: UserInternal, user_provided_otp: str, new_password: str = None,
                              update_password: bool = False) -> bool | dict[str, str | int]:
    """
        matches user provided OTP with password reset otp for user,
        if its a match, updatehashed password for user

        :param update_password:
        :param user: UserInternal
        :param user_provided_otp: the user provided OTP
        :param new_password: new plain text password

        :returns: boolean indicating whether if update hashed password was a success or not
    """

    log.info(f"verify_password_reset_otp(user={user}, user_provided_otp={user_provided_otp})")

    if not user.password_reset_verification_otp:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail='password reset otp not generated for user.'
        )

    if user.password_reset_verification_otp.otp != user_provided_otp:
        emsg = f"user provided OTP {user_provided_otp} and password reset OTP sent to user do not match."
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=emsg
        )
    log.info(f'USER FOUND: {user}, user provided TOP and user OTP matched.')
    if update_password is True:
        if not new_password:
            emsg = 'new password missing in request.'
            log.error(emsg)
            raise HTTPException(
                status_code=status.HTTP_206_PARTIAL_CONTENT,
                detail=emsg
            )
        log.info(f'update_password is {update_password}, changing users password and setting new password')
        new_hashed_password = generate_password_hash(new_password)
        update_user_data = UpdateUserInternal(hashed_password=new_hashed_password)
        return update_user(update_user_data, user)
    else:
        return {'status_code': 200, 'detail': 'OTP matched.'}
