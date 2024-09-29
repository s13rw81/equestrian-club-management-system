from pydantic import BaseModel
from typing import Optional

class GetPaymentDTO(BaseModel):
    payment_gateway_id: str
    payment_url: Optional[str] = None
    payment_status: str