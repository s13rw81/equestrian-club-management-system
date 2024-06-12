from typing import Annotated, Optional

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field

from data.db import PyObjectId


class TruckInternal(BaseModel):
    truck_type: str
    capacity: int
    special_features: str
    gps_equipped: bool
    air_conditioning: bool
    company_id: Optional[PyObjectId] = Field(alias="company_id")

    model_config = ConfigDict(arbitrary_types_allowed=True)


class TruckImages(BaseModel):
    url: AnyHttpUrl
    description: str = Field(max_length=200)
