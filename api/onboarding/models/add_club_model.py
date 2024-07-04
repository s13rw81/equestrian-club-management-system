from typing import Optional

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel, Field


class CreateClubRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    email_address: str = None
    phone_no: Optional[str] = None
    address: Optional[str] = None

