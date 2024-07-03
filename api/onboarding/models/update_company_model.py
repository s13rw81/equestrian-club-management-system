from typing import Optional, List

from models.generic_models.generic_address_model import Address
from models.generic_models.generic_contacts_model import Contact
from models.truck import TruckInternal
from pydantic import BaseModel


class UpdateCompanyModel(BaseModel):
    company_name: Optional[str] = None
    description: Optional[str] = None
    email: Optional[str] = None
    phone_no: Optional[str] = None
    is_khayyal_verified: Optional[bool] = None
    contact: Optional[Contact] = None
    address: Optional[Address] = None
    trucks: Optional[List[TruckInternal]] = []
    admins: Optional[list] = []
    images: Optional[list] = []
