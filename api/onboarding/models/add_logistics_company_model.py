from typing import Optional

from pydantic import BaseModel, field_validator
from validators.logistic_company.logistic_company_exists import check_logistic_company_email_exists


class CreatelogisticsCompanyRequest(BaseModel):
    email_address: str
    phone_no: str
    name: str
    description: Optional[str] = None

    @field_validator('email_address')
    def email_must_be_unique(cls, v):
        # Replace this with actual DB call
        existing = check_logistic_company_email_exists(v)
        if existing:
            raise ValueError(f"Email {v} already exists")
        return v
