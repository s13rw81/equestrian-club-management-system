from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field, field_serializer

from .enums import TransferStatus


class Transfers(BaseModel):
    customer_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    truck_id: str
    pickup_time: datetime
    status: TransferStatus
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

    @field_serializer("status")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
