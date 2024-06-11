from pydantic import BaseModel, field_serializer

from models.transfer.enums import TransferStatus


class ResponseCreateTransfer(BaseModel):
    transfer_id: str
    status: TransferStatus
    message: str

    @field_serializer("status")
    def enum_serializer(self, enum):
        return enum.value
