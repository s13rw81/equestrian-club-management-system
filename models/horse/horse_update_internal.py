from pydantic import BaseModel, validator
from typing import Optional, List


class UploadedBy(BaseModel):
    uploaded_by_id: Optional[str]
    uploaded_by_type: Optional[str]

class InternalUpdateSellHorse(BaseModel):
    name: Optional[str] = None
    year_of_birth: Optional[int] = None
    breed: Optional[str] = None
    size: Optional[str] = None
    gender: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

    @validator('year_of_birth', pre=True, always=True)
    def validate_year(cls, value):
        if value is not None:
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            if not (1900 <= value <= 2100):
                raise ValueError('Year of birth must be between 1900 and 2100')
        return value

    @validator('price', pre=True, always=True)
    def validate_price(cls, value):
        if value is not None:
            try:
                value = float(value)
            except ValueError:
                raise ValueError('Price must be a positive number')
            if value < 0:
                raise ValueError('Price must be a positive number')
        return value
