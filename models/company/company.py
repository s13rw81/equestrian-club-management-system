from typing import List

from pydantic import BaseModel

from models.truck import Truck


class Company(BaseModel):
    company_name: str
    admin_id: str
    trucks: List[Truck]
