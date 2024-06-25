from pydantic import BaseModel, Field
from typing import Optional, List
from bson import ObjectId


class Provider(BaseModel):
    provider_id: str
    provider_type: str


class HorseSellingServiceInternal(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    horse_id: str
    name: str
    year_of_birth: int
    breed: str
    size: int
    gender: str
    description: str
    images: List[str]
    provider: Provider
    price_sar: int
