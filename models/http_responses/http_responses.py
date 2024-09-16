from pydantic import BaseModel
from typing import Optional, Any

class Success(BaseModel):
    status: int
    message: str
    data: Optional[Any] = None

class Failure(BaseModel):
    status: int
    message: str
    data: Optional[Any] = None