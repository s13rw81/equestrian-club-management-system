from typing import Optional, List

from bson import ObjectId
from data.db import PyObjectId
from pydantic import BaseModel, Field


class LogisticCompanyInternal(BaseModel):
    id: Optional[PyObjectId] = Field(alias = '_id', default = None)
    email_address: str
    phone_no: str
    name: str = Field(..., min_length = 1)
    description: Optional[str] = Field(None, max_length = 500)
    is_khayyal_verified: bool = False
    images: Optional[List[str]] = []
    users: Optional[List] = []

    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
        json_encoders = {ObjectId: str}
