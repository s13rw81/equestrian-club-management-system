from pydantic import BaseModel, EmailStr, HttpUrl
from decimal import Decimal


class CreatePaymentDTO(BaseModel):
    amount: Decimal
    customer_name: str
    customer_email: EmailStr
    payment_event_webhook: HttpUrl
    redirect_url: HttpUrl

