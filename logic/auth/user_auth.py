from data.dbapis.user.read_queries import get_user_by_email, get_user_by_phone_number
from .password_hash_utility import verify_password
from models.user import UserInternal
from datetime import timedelta, datetime, timezone
from config import JWT_TOKEN_EXPIRY_IN_DAYS, JWT_SECRET_KEY, JWT_ALGORITHM
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from typing import Annotated, Optional
from logging_config import log
from validators.regex_validators import is_valid_email

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    log.info(f"create_access_token invoked: data={data}")

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=JWT_TOKEN_EXPIRY_IN_DAYS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    log.info(f"returning {encoded_jwt}")

    return encoded_jwt


def authenticate_user(
        plain_password: str,
        email: Optional[str] = None,
        phone_number: Optional[str] = None
) -> UserInternal | None:
    log.info(f"authenticate_user invoked: email={email}, phone_number={phone_number}")

    user = get_user_by_email(email=email) if email else get_user_by_phone_number(phone_number=phone_number)

    if user is None:
        return None

    is_verified = verify_password(plain_password=plain_password, hashed_password=user.hashed_password)

    log.info(f"is_verified = {is_verified}")

    retval = user if is_verified else None

    log.info(f"returning {retval}")

    return retval


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserInternal | None:
    log.info(f"get_current_user invoked: token={token}")

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )

    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        sub: str = payload.get("sub")

        if sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    retval = (get_user_by_email(email=sub) if is_valid_email(email=sub) else
              get_user_by_phone_number(phone_number=sub))

    log.info(f"returning {retval}")

    return retval
