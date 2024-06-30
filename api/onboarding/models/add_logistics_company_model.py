from typing import Optional

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from pydantic import BaseModel


class CreatelogisticsCompanyRequest(BaseModel):
    company_name: str
    description: Optional[str] = None
    contact: Optional[Contact] = None
    address: Optional[Address] = None
    # trucks: List[TruckInternal] = None
