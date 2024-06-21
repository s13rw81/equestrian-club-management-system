from pydantic import BaseModel
from typing import Optional

class ResponseModel(BaseModel):
    success: bool
    message: str
    item_id: Optional[str]
