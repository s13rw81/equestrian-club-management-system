from typing import Annotated, Optional

from api.auth.models.reset_password_verify import ResetPasswordVerify
from data.dbapis.user.read_queries import get_user_by_email, get_user_by_phone_number
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from logging_config import log
from logic.auth import authenticate_user, create_access_token, get_current_user
from logic.auth.otp_management import send_sign_up_otp, verify_sign_up_otp, send_reset_password_otp, \
    verify_password_reset_otp
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
        msg = 'password reset otp sent'
        log.info(msg)
        return {"status": "OK", "detail": msg}
    else:
        emsg = 'error when sending password reset otp'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=emsg
        )


@user_auth_router.post("/reset-password-verify-otp")
async def reset_password_verify_otp(request: ResetPasswordVerify):
    log.info(f"updating password for : {request}")  # TODO: check how this looks in the actual log file
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
    if email_address:
        user = get_user_by_email(email=email_address)

    if phone_number:
        user = get_user_by_phone_number(phone_number=phone_number)

    if not user:
        emsg = f'no user found with email_address : {email_address} or phone_number : {phone_number}'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )
    result = verify_password_reset_otp(user=user, user_provided_otp=user_provided_otp, new_password=new_password)

    if result:
        return {"status_code": 200, "status": "OK", "detail": 'reset password success for user.'}


@user_auth_router.put("/reset-password-update-password")
async def reset_password_update_password(request: ResetPasswordVerify):
    log.info(f"updating password for : {request}")  # TODO: check how this looks in the actual log file
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
    if email_address:
        user = get_user_by_email(email=email_address)

    if phone_number:
        user = get_user_by_phone_number(phone_number=phone_number)

    if not user:
        emsg = f'no user found with email_address : {email_address} or phone_number : {phone_number}'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )
    result = verify_password_reset_otp(user=user, user_provided_otp=user_provided_otp, new_password=new_password, update_password = True)

    if result:
        return {"status_code": 200, "status": "OK", "detail": 'reset password success for user.'}
