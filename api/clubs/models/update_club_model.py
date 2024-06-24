from datetime import datetime
from typing import Optional, List

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from models.user.user_external import UserExternal
from pydantic import BaseModel, Field


class UpdateClubRequest(BaseModel):
    name: str = Field(..., min_length = 1)
    description: Optional[str] = Field(None, max_length = 500)
    price: Optional[float] = Field(..., gt = 0)
    address: Optional[Address] = None
    contact: Optional[Contact] = None
    creation_date_time: Optional[datetime] = None
    update_date_time: Optional[datetime] = None
    image_urls: Optional[List[str]] = None
    admins: Optional[List[UserExternal]] = list()
