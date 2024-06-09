from models.user import UserInternal
from data.db import get_users_collection
from logging_config import log

users_collection = get_users_collection()


def get_user_by_email(email: str) -> UserInternal | None:
    """
            if user exists for the provided email
            returns the User, otherwise None

            :param email: str
            :returns: User if exists otherwise None
    """

    log.info(f"get_user_by_email invoked: email={email}")

    user = users_collection.find_one({"email_address": email})

    if user is None:
        retval = None
    else:
        retval = UserInternal(**user)

    log.info(f"returning {retval}")

    return retval


def get_user_by_phone_number(phone_number: str) -> UserInternal | None:
    """
            if user exists for the provided phone_number
            returns the User, otherwise None

            :param phone_number: str
            :returns: User if exists otherwise None
    """

    log.info(f"get_user_by_phone_number invoked: email={phone_number}")

    user = users_collection.find_one({"phone_number": phone_number})

    if user is None:
        retval = None
    else:
        retval = UserInternal(**user)

    log.info(f"returning {retval}")

    return retval
