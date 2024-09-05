from typing import Optional

from bson import ObjectId
from pydantic import BaseModel


class UserExternal(BaseModel):
    id: Optional[str] = None
    full_name: str
    user_role: str
    email_address: str

    class Config:
        json_encoders = {ObjectId: str}
