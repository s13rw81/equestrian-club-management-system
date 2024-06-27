from typing import Optional, List

from bson import ObjectId
from data.db import PyObjectId
from models.logistics_company_services import Provider
from pydantic import BaseModel, Field


class RidingLessonService(BaseModel):
    id: Optional[PyObjectId] = Field(alias = '_id', default = None)
    description: Optional[str] = Field(default = 'horse riding service.')
    provider: Provider
    price: float
    trainers: Optional[List[str]] = list()

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
