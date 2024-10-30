from typing import Annotated
from data.dbapis.user import find_user, update_user
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from logging_config import log
from logic.auth import (
    authenticate_user,
    create_access_token,
    send_sign_up_otp,
    send_reset_password_otp,
    verify_reset_password_otp,
    generate_password_hash
)
from models.http_responses import Success
from models.user import UpdateUserInternal
from .models import (
    Token,
    GenerateSignUpOtpDTO,
    GenerateResetPasswordOtpDTO,
    ResetPasswordDTO,
    ResetPasswordVerifyOtpDTO
)
from datetime import datetime
import pytz
import phonenumbers

user_auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@user_auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    log.info(f"inside auth/token username={form_data.username}")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        log.info("trying to parse phone number")
        phone_number = phonenumbers.parse(form_data.username)
        phone_number = phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    except phonenumbers.NumberParseException:
        log.info("failed to parse phone number, raising exception...")
        raise credentials_exception

    user = authenticate_user(
        phone_number=phone_number,
        plain_password=form_data.password
    )

    if not user:
        raise credentials_exception

    access_token = create_access_token(data={"sub": user.email_address if user.email_address else user.phone_number})

    retval = Token(
        access_token=access_token,
        token_type="Bearer"
    )

    log.info(f"returning {retval}")

    return retval


@user_auth_router.post("/generate-sign-up-otp")
async def generate_sign_up_otp(generate_sign_up_otp_dto: GenerateSignUpOtpDTO):
    log.info(f"inside auth/generate-sign-up-otp (generate_sign_up_otp_dto={generate_sign_up_otp_dto})")

    result = send_sign_up_otp(
        email_address=generate_sign_up_otp_dto.email_address,
        phone_number=generate_sign_up_otp_dto.phone_number
    )

    if result:
        log.info("OTP sent successfully... returning success response...")
        return Success(
            message="OTP generated successfully..."
        )
    else:
        log.info("failed to send OTP, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not send otp"
        )

@user_auth_router.post("/generate-reset-password-otp")
async def generate_reset_password_otp(generate_reset_password_otp_dto: GenerateResetPasswordOtpDTO):
    log.info(f"inside auth/generate-reset-password-otp ("
             f"generate_reset_password_otp_dto={generate_reset_password_otp_dto})")

    result = send_reset_password_otp(
        email_address=generate_reset_password_otp_dto.email_address,
        phone_number=generate_reset_password_otp_dto.phone_number
    )

    if result:
        log.info("OTP sent successfully... returning success response...")
        return Success(
            message="OTP generated successfully..."
        )
    else:
        log.info("failed to send OTP, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not send otp"
        )


@user_auth_router.post("/reset-password-verify-otp")
async def reset_password_verify_otp(reset_password_verify_otp_dto: ResetPasswordVerifyOtpDTO):
    log.info(f"inside /auth/reset-password-verify-otp (reset_password_verify_otp_dto={reset_password_verify_otp_dto})")

    verification_result = verify_reset_password_otp(
        user_provided_otp=reset_password_verify_otp_dto.otp,
        email_address=reset_password_verify_otp_dto.email_address,
        phone_number=reset_password_verify_otp_dto.phone_number
    )

    log.info(f"otp verification result = {verification_result}")
    return Success(
        message="success" if verification_result else "failed",
        data={
            "is_valid_otp": verification_result
        }
    )


@user_auth_router.put("/reset-password-update-password")
async def reset_password_update_password(reset_password_dto: ResetPasswordDTO):

    log.info(f"inside /auth/reset-password-update-password (reset_password_dto={reset_password_dto})")

    email_address = reset_password_dto.email_address
    phone_number = reset_password_dto.phone_number

    user = find_user(email_address=email_address) if email_address else find_user(phone_number=phone_number)


    if not user:
        emsg = f'no user found with email_address : {email_address} or phone_number : {phone_number}'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )

    verification_result = verify_reset_password_otp(
        user_provided_otp=reset_password_dto.otp,
        email_address=reset_password_dto.email_address,
        phone_number=reset_password_dto.phone_number
    )

    if not verification_result:
        log.info("invalid OTP, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="invalid OTP"
        )

    log.info("OTP validated successfully... updating password in the database...")

    update_user_dto = UpdateUserInternal(
        id=user.id,
        last_updated_on=datetime.now(pytz.utc),
        hashed_password=generate_password_hash(reset_password_dto.new_password)
    )

    update_result = update_user(update_user_dto=update_user_dto)

    log.info(f"update executed, result = {update_result}")

    return Success(
        message="password updated successfully"
    )