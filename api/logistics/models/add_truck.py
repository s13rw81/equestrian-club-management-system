from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from data.db import PyObjectId


class AddTruck(BaseModel):
    truck_type: str
    capacity: str
    special_features: str = Field(max_length=200)
    gps_equipped: bool
    air_conditioning: bool
    company_id: Optional[PyObjectId] = Field(alias="company_id")

    model_config = ConfigDict(arbitrary_types_allowed=True)
