import json
from typing import List

from pydantic import BaseModel, model_validator


class UploadTruckImages(BaseModel):
    description: List[str]

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
