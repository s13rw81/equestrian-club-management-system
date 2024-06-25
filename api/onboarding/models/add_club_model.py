from typing import Optional

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel, Field


class CreateClubRequest(BaseModel):
    name: str = Field(..., min_length = 1)
    description: Optional[str] = Field(None, max_length = 500)
    price: Optional[float] = Field(..., gt = 0)
    address: Optional[Address] = []
    contact: Optional[Contact] = []
