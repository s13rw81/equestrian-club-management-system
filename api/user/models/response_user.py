from pydantic import BaseModel
from typing import Optional


class ResponseUser(BaseModel):
    first_name: str
    last_name: str
    email_address: str
    phone_number: Optional[str] = None
    otp_verified: bool
