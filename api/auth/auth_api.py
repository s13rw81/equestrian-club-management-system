from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .models import Token
from models.user import UserInternal
from logic.auth import authenticate_user, create_access_token, get_current_user
from logic.auth.otp_management import send_sign_up_otp, verify_sign_up_otp
from logging_config import log
from validators.regex_validators import is_valid_email

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



