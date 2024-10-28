from pydantic import BaseModel, field_validator, model_validator
from data.dbapis.reset_password_otp import find_reset_password_otp
from config import log
from typing import Optional
from typing_extensions import Self
import phonenumbers

class ResetPasswordVerifyOtpDTO(BaseModel):
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    otp: str

    @field_validator("phone_number")
    def validate_phone_number(cls, phone_number):

        if not phone_number:
            return phone_number

        log.info(f"validating phone number in ResetPasswordVerifyOtpDTO(phone_number={phone_number})")

        error = ValueError(f"invalid phone number (phone_number={phone_number})")

        try:
            parsed_phone_number = phonenumbers.parse(phone_number)
        except phonenumbers.NumberParseException:
            log.info(f"failed to parse phone number, raising error (phone_number={phone_number})")
            raise error

        if not phonenumbers.is_valid_number(parsed_phone_number):
            log.info(f"phone number is not valid, raising error (phone_number={phone_number})")
            raise error

        phone_number_formatted = phonenumbers.format_number(
            parsed_phone_number,
            phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )

        return phone_number_formatted

    @model_validator(mode="after")
    def check_whether_either_email_or_phone_provided(self) -> Self:

        email_address = self.email_address
        phone_number = self.phone_number

        # CHECK 1: check whether either email or phone provided
        if email_address and phone_number:
            log.info("email_address and phone_number cannot be present simultaneously, raising ValueError")
            raise ValueError("email_address and phone_number cannot be present simultaneously")

        if not (email_address or phone_number):
            log.info("either email_address or phone_number must be present, raising ValueError")
            raise ValueError("either email_address or phone_number must be present, raising ValueError")

        # CHECK 2: check whether reset password otp exists
        reset_password_otp = (find_reset_password_otp(email_address=email_address)
                              if email_address else find_reset_password_otp(phone_number=phone_number))

        if not reset_password_otp:
            log.info("no reset_password_otp exists for the provided credential, raising ValueError")
            raise ValueError("please generate reset_password_otp first")

        return self