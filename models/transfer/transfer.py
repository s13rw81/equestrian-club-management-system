from datetime import datetime

from pydantic import BaseModel, Field

from utils.date_time import get_current_utc_datetime

from .enums import TransferStatus


class TransfersInternal(BaseModel):
    customer_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    truck_id: str
    pickup_time: datetime
    status: TransferStatus
    created_at: datetime = Field(default_factory=lambda: get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=lambda: get_current_utc_datetime)
