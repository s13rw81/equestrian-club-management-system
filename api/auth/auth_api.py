from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from .models import Token
from models.user import UserInternal
# from models.validation_response import ValidationResponse
from logic.auth import authenticate_user, create_access_token, get_current_user
from logic.auth.otp_management import send_email_verification_otp_logic, verify_email_verification_otp_logic
from logging_config import log
from validators.user import whether_user_exists
from validators.regex_validators import is_valid_email

user_auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@user_auth_router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]) -> Token:
    log.info(f"/token invoked: username={form_data.username}")

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
