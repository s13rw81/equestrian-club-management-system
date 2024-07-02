from typing import Optional
from pydantic import BaseModel


class ResetPasswordVerify(BaseModel):

    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    otp: str
    new_password: Optional[str] = None
