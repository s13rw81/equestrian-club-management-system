from typing import List

from pydantic import AnyHttpUrl, BaseModel, Field

from data.db import PyObjectId


class TruckImages(BaseModel):
    url: AnyHttpUrl
    description: str = Field(max_length=200)


class ResponseTruckDetails(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    truck_type: str
    availability: str
    images: List[TruckImages]
