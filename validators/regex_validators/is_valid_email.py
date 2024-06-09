import re
from logging_config import log


def is_valid_email(email: str) -> bool:

    """
    returns True if it's a valid email address, false otherwise
    :param email: the string to be checked
    :return: True if it's a valid email address, false otherwise
    """

    log.info(f"inside is_valid_email(email={email})")
    email_regex = re.compile(
        r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    )
    return re.match(email_regex, email) is not None
