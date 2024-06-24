from typing import Optional
from pydantic import BaseModel


class ResetPasswordVerify(BaseModel):
    otp: str
    email_address: Optional[str] = None
    phone_number: Optional[str] = None
    new_password: Optional[str]
