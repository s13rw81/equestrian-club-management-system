from typing import List, Optional

from bson import ObjectId
from data.db import PyObjectId
from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel, Field

from models.truck import TruckInternal


class Company(BaseModel):
    id: Optional[PyObjectId] = Field(alias='_id', default=None)
    company_name: str
    description: Optional[str] = None
    contact: Optional[Contact] = None
    address: Optional[Address] = None
    trucks: List[TruckInternal] = []
    admins: Optional[list] = []

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
