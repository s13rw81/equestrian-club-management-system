from pydantic import BaseModel, field_serializer

from models.transfer.enums import TransferStatus


class CreateCustomerTransfer(BaseModel):
    customer_id: str
    truck_id: str
    source_location: str
    destination_location: str


class ResponseCreateCustomerTransfer(BaseModel):
    transfer_id: str
    status: TransferStatus

    @field_serializer("status")
    def enum_serializer(self, enum):
        return enum.value
