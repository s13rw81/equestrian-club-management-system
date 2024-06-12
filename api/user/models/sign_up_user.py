from pydantic import BaseModel, field_validator, Field, model_validator
from typing import Optional
from typing_extensions import Self
from models.user.enums import RidingStage, HorseOwnership, EquestrianDiscipline
from validators.user import whether_user_exists
from validators.regex_validators import is_valid_email


class SignUpUser(BaseModel):
    full_name: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    password: str = Field(exclude=True)
    riding_stage: RidingStage
    horse_ownership_status: HorseOwnership
    equestrian_discipline: EquestrianDiscipline

    @field_validator("email_address")
    @classmethod
    def email_address_validator(cls, email: Optional[str]) -> Optional[str]:

        if email is None:
            return email

        if not is_valid_email(email=email):
            raise ValueError("not a valid email address...")

        result = whether_user_exists(email=email)

        if result:
            raise ValueError("email already exists...")

        return email

    @field_validator("phone_number")
    @classmethod
    def email_validator(cls, phone_number: Optional[str]) -> Optional[str]:

        if phone_number is None:
            return phone_number

        result = whether_user_exists(phone=phone_number)

        if result:
            raise ValueError("phone_number already exists...")

        return phone_number

    @field_validator("password")
    @classmethod
    def password_validator(cls, password: str) -> str:
        password = password.strip()

        if len(password) < 6:
            raise ValueError("password should be more than 5 characters...")

        return password

    @model_validator(mode="after")
    def check_whether_email_and_phone_both_are_present(self) -> Self:
        # email_address and phone_number both are present
        if self.email_address and self.phone_number:
            raise ValueError("either email_address or phone_number should be present not both!")

        # neither email_address nor phone_number is present
        if not (self.email_address or self.phone_number):
            raise ValueError("either email_address or phone_number must be present!")

        return self