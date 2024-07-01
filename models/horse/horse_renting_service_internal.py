from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId
from models.logistics_company_services.logistics_company_services import Provider


class HorseRentingServiceInternal(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    horse_id: str
    name: str
    year_of_birth: int
    breed: str
    size: int
    gender: str
    description: str
    provider: Provider
    price_sar: int

