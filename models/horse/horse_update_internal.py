from pydantic import BaseModel
from typing import Optional, List


class UploadedBy(BaseModel):
    uploaded_by_id: Optional[str]
    uploaded_by_type: Optional[str]


class InternalUpdateSellHorse(BaseModel):
    name: Optional[str]
    year_of_birth: Optional[int]
    breed: Optional[str]
    sire: Optional[str]
    gender: Optional[str]
    description: Optional[str]
    price_sar: Optional[int]
    uploaded_by: Optional[UploadedBy]
