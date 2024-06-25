from typing import Optional

from pydantic import BaseModel


class UserExternal(BaseModel):
    id: Optional[str] = None
    full_name: str
    user_role: str
    email_address: str
