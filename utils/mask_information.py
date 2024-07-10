from typing import Union


def mask_phone_number(phone_number: Union[str, None]) -> Union[str, None]:
    """mask the phone number without extension"""
    mask_number = "X" * 10
    return f"{phone_number[:3]}{mask_number}" if phone_number else None


def mask_email(email: Union[str, None]) -> Union[str, None]:
    """return masked email identifier with email provider"""
    if not email:
        return None
    email_split = email.split("@")
    mask = (len(email_split[0]) - 1) * "X"
    masked_email = f"{email[0]}{mask}@{email_split[-1]}"
    return masked_email
