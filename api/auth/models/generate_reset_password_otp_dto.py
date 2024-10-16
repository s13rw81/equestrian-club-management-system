from pydantic import BaseModel, EmailStr, field_validator, model_validator
from typing import Optional
from typing_extensions import Self
from logging_config import log
import phonenumbers
from data.dbapis.user import find_user


class GenerateResetPasswordOtpDTO(BaseModel):
    email_address: Optional[EmailStr] = None
    phone_number: Optional[str] = None

    @field_validator("email_address")
    def validate_email_address(cls, email_address):
        if not email_address:
            return email_address

        log.info(f"validating email_address in GenerateResetPasswordOtpDTO(email_address={email_address})")

        user = find_user(email_address=email_address)

        if not user:
            log.info(f"email_address: {email_address} is not registered, raising ValueError...")
            raise ValueError(f"email_address: {email_address} is not registered...")

        return email_address

    @field_validator("phone_number")
    def validate_phone_number(cls, phone_number):

        if not phone_number:
            return phone_number

        log.info(f"validating phone number in GenerateResetPasswordOtpDTO(phone_number={phone_number})")

        error = ValueError(f"invalid phone number (phone_number={phone_number})")

        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            log.info(f"failed to parse phone number, raising error (phone_number={phone_number})")
            raise error

        if not phonenumbers.is_valid_number(parsed_phone_number):
            log.info(f"phone number is not valid, raising error (phone_number={phone_number})")
            raise error

        phone_number_formatted =  phonenumbers.format_number(
            parsed_phone_number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        user = find_user(phone_number=phone_number_formatted)

        if not user:
            log.info(f"phone_number: {phone_number_formatted}, is not registered... raising ValueError")
            raise ValueError(f"phone_number: {phone_number_formatted}, is not registered...")

        return phone_number_formatted

    @model_validator(mode="after")
    def check_whether_either_email_or_phone_provided(self) -> Self:

        email_address = self.email_address
        phone_number = self.phone_number

        if email_address and phone_number:
            log.info("email_address and phone_number cannot be present simultaneously, raising ValueError")
            raise ValueError("email_address and phone_number cannot be present simultaneously")

        if not (email_address or phone_number):
            log.info("either email_address or phone_number must be present, raising ValueError")
            raise ValueError("either email_address or phone_number must be present, raising ValueError")

        return self