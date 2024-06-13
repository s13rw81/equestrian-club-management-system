from typing import List

from pydantic import BaseModel, Field

from data.db import PyObjectId


class ViewTruckResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str
    availability: str
