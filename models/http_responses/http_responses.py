from pydantic import BaseModel
from typing import Optional, Any

class Success(BaseModel):
    message: str
    data: Optional[Any] = None