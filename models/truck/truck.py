from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from data.db import PyObjectId
from utils.date_time import get_current_utc_datetime

from .enums import TruckAvailability


class TruckImages(BaseModel):
    image_key: str
    description: str = Field(max_length=200)


class TruckInternal(BaseModel):
    truck_type: str
    capacity: int
    gps_equipped: bool
    special_features: str = Field(max_length=200)
    air_conditioning: bool
    company_id: Optional[PyObjectId] = Field(alias="company_id")
    name: str = ""
    availability: TruckAvailability = TruckAvailability.UN_AVAILABLE.value
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)
    images: List[TruckImages] = []

    model_config = ConfigDict(arbitrary_types_allowed=True)
