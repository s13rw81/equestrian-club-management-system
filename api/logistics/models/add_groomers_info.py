from pydantic import BaseModel


class GroomersInfo(BaseModel):
    customer_transfer_id: str
    groomer_name: str
    contact_number: str


class ResponseGroomersInfo(BaseModel):
    info_id: str
