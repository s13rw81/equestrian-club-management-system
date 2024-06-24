from typing import Optional

from pydantic import BaseModel, Field


class Location(BaseModel):
    lon: float
    lat: float


class Address(BaseModel):
    address_line_1: Optional[str] = Field(None, min_length = 0)
    address_line_2: Optional[str] = Field(None, min_length = 0)
    city: str = Field(..., min_length = 1)
    state_province: str = Field(..., min_length = 1)
    country: str = Field(..., min_length = 1)
    zip: Optional[int] = Field(None, ge = 1000, le = 999999999)
    location: Optional[Location] = list()
