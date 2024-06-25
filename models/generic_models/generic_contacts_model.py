from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, HttpUrl, field_validator
from validators.regex_validators import is_valid_email


class PhoneType(str, Enum):
    OFFICE = "Office"
    MOBILE = "Mobile"
    LANDLINE = "Landline"
    FAX = "Fax"


class PhoneDetails(BaseModel):
    code: str
    number: str


class PhoneNumber(BaseModel):
    number: PhoneDetails
    type: PhoneType


class Contact(BaseModel):
    phone_numbers: Optional[List[PhoneNumber]] = []
    emails: Optional[List[str]] = []
    website_url: Optional[str] = []

    @field_validator('phone_numbers')
    def validate_phone_numbers(cls, v):
        if v and len(v) > 5:
            raise ValueError('Cannot have more than 5 phone numbers')
        return v

    @field_validator('emails')
    def validate_emails(cls, v):
        if v and len(v) > 3:
            raise ValueError('Cannot have more than 3 email addresses')
        for email in v:
            cls.email_address_validator(email)
        return v

    @staticmethod
    def email_address_validator(email: Optional[str]) -> Optional[str]:
        if email is None:
            return email

        if not is_valid_email(email = email):
            raise ValueError("not a valid email address...")

        return email
