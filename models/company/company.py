from typing import List

from pydantic import BaseModel

from models.truck import TruckInternal


class Company(BaseModel):
    company_name: str
    admin_id: str
    trucks: List[TruckInternal]
