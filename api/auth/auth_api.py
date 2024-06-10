from typing import Annotated, Optional

from api.auth.models.reset_password_verify import ResetPasswordVerify
from data.dbapis.user.read_queries import get_user_by_email, get_user_by_phone_number, get_user_by_otp
from data.dbapis.user.write_queries import update_user_password
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from logging_config import log
from logic.auth import authenticate_user, create_access_token, get_current_user, generate_password_hash
from logic.auth.otp_management import send_sign_up_otp, verify_sign_up_otp, send_reset_password_otp
from models.user import UserInternal
from validators.regex_validators import is_valid_email

from .models import Token

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

    user = authenticate_user(
        email=form_data.username,
        plain_password=form_data.password
    ) if is_valid_email(email=form_data.username) else authenticate_user(
        phone_number=form_data.username,
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
async def send_otp_for_email_verification(user: Annotated[UserInternal, Depends(get_current_user)]):
    log.info(f"inside auth/generate-sign-up-otp (user={user})")

    result = send_sign_up_otp(user=user)

    if result:
        return {"status": "OK"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not send otp"
        )


@user_auth_router.post("/verify-sign-up-otp")
async def verify_email_verification_otp(
        user: Annotated[UserInternal, Depends(get_current_user)],
        user_provided_otp: str
):
    log.info(f"auth/verify-sign-up-otp(user={user}, user_provided_otp={user_provided_otp})")

    result = verify_sign_up_otp(
        user=user,
        user_provided_otp=user_provided_otp
    )

    if result:
        return {"status": "OK"}
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not send otp"
        )


@user_auth_router.post("/reset-password-request")
async def reset_password(email_address: Optional[str] = None, phone_number: Optional[str] = None):
    # TODO: refactor this check
    if email_address and phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone should be passed not both"
        )

    if not (email_address or phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone must be passed"
        )

    user = (get_user_by_phone_number(phone_number=phone_number) if phone_number else
            get_user_by_email(email=email_address))

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="user with provided email or phone number not found."
        )

    retval = send_reset_password_otp(user=user)
    if retval:
        log.info('password reset otp sent')
        return {"status": "OK", "detail": 'reset password OTP sent to user.'}
    else:
        log.error('error when sending password reset otp')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not send otp"
        )


@user_auth_router.post("/reset-password-verify")
async def reset_password_verify(request: ResetPasswordVerify):
    email_address = request.email_address
    phone_number = request.phone_number
    new_password = request.new_password
    user_provided_otp = request.otp

    # TODO: refactor this check
    if email_address and phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone should be passed not both"
        )

    if not (email_address or phone_number):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="either email or phone must be passed"
        )
    user = get_user_by_otp(otp=user_provided_otp)
    if user:
        if user.email_address == email_address:
            log.info(f'USER FOUND: {user}, user provided email and user email matched.')
            new_hashed_password = generate_password_hash(new_password)
            result = update_user_password(new_hashed_password, user)
            if result:
                return {"status_code": 200, "status": "OK", "detail": 'reset password success for user.'}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="user provided email and OPT user email do not match."
            )
    else:
        log.error(f'OTP : {user_provided_otp} does not match any user')
