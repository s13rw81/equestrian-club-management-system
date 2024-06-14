from typing import Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from data.db import PyObjectId

from .enums import TruckAvailability


class TruckInternal(BaseModel):
    truck_type: str
    capacity: int
    gps_equipped: bool
    special_features: str = Field(max_length=200)
    air_conditioning: bool
    company_id: Optional[PyObjectId] = Field(alias="company_id")
    name: str = ""
    availability: TruckAvailability = TruckAvailability.UN_AVAILABLE.value

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TruckImages(BaseModel):
    url: AnyHttpUrl
    description: str = Field(max_length=200)
