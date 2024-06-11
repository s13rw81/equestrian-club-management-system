from pydantic import BaseModel, field_serializer

from models.transfer.enums import TransferStatus


class UpdateTransferStatus(BaseModel):
    status: TransferStatus

    @field_serializer("status")
    def enum_serializer(self, enum):
        return enum.value
