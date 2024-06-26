from bson import ObjectId
from pydantic import BaseModel, Field
from typing import Optional, List


class UploadedBy(BaseModel):
    uploaded_by_id: str
    uploaded_by_type: str


class InternalSellHorse(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    name: str
    year_of_birth: int
    breed: str
    size: int
    gender: str
    description: str
    images: List[str]
    uploaded_by: UploadedBy
