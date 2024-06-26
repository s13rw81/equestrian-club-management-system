from pydantic import BaseModel, Field
from typing import Optional, List


class UploadedBy(BaseModel):
    uploaded_by_id: Optional[str] = Field(None, example="1234")
    uploaded_by_type: Optional[str] = Field(None, example="user")


class HorseSellUpdate(BaseModel):
    name: Optional[str] = Field(None, example="Bobby")
    year_of_birth: Optional[int] = Field(None, example=2017)
    breed: Optional[str] = Field(None, example="Thoroughbred")
    size: Optional[int] = Field(None, example=150000)
    gender: Optional[str] = Field(None, example="Gelding")
    description: Optional[str] = Field(None, example="Bobby is well-behaved and has excellent ring qualities.")
    images: Optional[List[str]] = Field(None, example=["http://example.com/image1.jpg", "http://example.com/image2.jpg"])
    uploaded_by: Optional[UploadedBy] = Field(None)
