from datetime import datetime
from typing import Optional

from models.generic_models.generic_address_model import Address
from pydantic import BaseModel


# TODO: make payment a generic model

class BookRidinglessonRequest(BaseModel):
    lesson_service: str
    rider: str
    trainer: str
    lesson_datetime: datetime
    venue: Optional[Address] = None
    payment_status: Optional[str] = None  # TODO: change to an ENUM
    booking_status: str  # TODO: change to an ENUM
