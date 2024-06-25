from pydantic import Field
from datetime import datetime
from typing import Optional, List

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from models.user.user_external import UserExternal
from pydantic import BaseModel


class ClubExternal(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str]
    price: Optional[float]
    address: Optional[Address]
    contact: Optional[Contact]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    image_urls: Optional[List[str]]
    admins: Optional[List[UserExternal]]
