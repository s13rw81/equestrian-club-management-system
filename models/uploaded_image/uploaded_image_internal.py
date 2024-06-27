from pydantic import BaseModel, Field
from data.db import PyObjectId
from typing import Optional


class UploadedImageInternal(BaseModel):
    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    image_path: str
