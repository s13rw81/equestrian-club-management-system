from datetime import datetime

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from utils.date_time import get_current_utc_datetime

from .enums import TransferStatus


# this is for transfer of horses between clubs
class TransfersInternal(BaseModel):
    customer_id: str
    horse_id: str
    source_club_id: str
    destination_club_id: str
    logistics_company_id: str
    truck_id: str
    pickup_time: datetime
    status: TransferStatus
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)

    @field_serializer("status")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value


class TransfersInternalWithID(TransfersInternal):
    transfer_id: str


# this would be for the customer requested transfers
class CustomersTransfersInternal(BaseModel):
    customer_id: str
    source_location: str
    destination_location: str
    logistics_company_id: str
    truck_id: str
    status: TransferStatus
    created_at: datetime = Field(default_factory=get_current_utc_datetime)
    updated_at: datetime = Field(default_factory=get_current_utc_datetime)

    @field_serializer("status")
    def enum_serializer(self, enum):
        if not enum:
            return

        return enum.value
