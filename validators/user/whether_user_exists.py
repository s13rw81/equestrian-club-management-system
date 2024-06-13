from typing import Optional

from data.dbapis.user.read_queries import get_user_by_email, get_user_by_phone_number
from logging_config import log


def whether_user_exists(email: Optional[str] = None, phone: Optional[str] = None) -> bool:
    log.info(f"inside whether_user_exists(email={email}, phone={phone})")

    if email and phone:
        raise ValueError("either email or phone should be passed not both")

    if not (email or phone):
        raise ValueError("either email or phone must be passed")

    result = get_user_by_email(email=email) if email else get_user_by_phone_number(phone_number=phone)

    return result is not None
