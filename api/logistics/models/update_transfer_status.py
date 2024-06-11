from datetime import datetime

from pydantic import BaseModel, computed_field, field_serializer

from models.transfer.enums import TransferStatus
from utils.date_time import get_current_utc_datetime


class UpdateTransferStatus(BaseModel):
    status: TransferStatus

    @field_serializer("status")
    def enum_serializer(self, enum):
        return enum.value

    @computed_field
    @property
    def updated_at(self) -> datetime:
        return get_current_utc_datetime()
