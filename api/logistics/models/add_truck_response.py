from pydantic import BaseModel


class AddTruckResponse(BaseModel):
    success: bool
    truck_id: str
    message: str
