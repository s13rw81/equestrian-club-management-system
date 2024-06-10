from datetime import datetime
from typing import Optional

from pydantic import BaseModel, field_validator

from data.dbapis.user.read_queries import get_user_by_object_id


class CreateTransfer(BaseModel):
    customer_id: str
    horse_id: str
    destination_club_id: str
    logistics_company_id: str
    truck_id: str
    pickup_time: str

    @field_validator("pickup_time")
    def parse_date(cls, pickup_time: Optional[str]) -> Optional[datetime]:
        try:
            return datetime.fromisoformat(pickup_time)
        except ValueError:
            raise ValueError("Incorrect date format provided.")

    @field_validator("customer_id")
    def validate_customer_id(cls, customer_id: str) -> Optional[str]:
        user = get_user_by_object_id(user_id=customer_id)
        if not user:
            raise ValueError("Incorrect customer_id provided.")
        return customer_id

    @field_validator("horse_id")
    def validate_horse_id(cls, horse_id: str) -> Optional[str]:
        return horse_id

    @field_validator("destination_club_id")
    def validate_destination_club_id(
        cls, destination_club_id: Optional[str]
    ) -> Optional[str]:
        return destination_club_id

    @field_validator("logistics_company_id")
    def validate_logsitics_company_id(cls, logistics_company_id: str) -> Optional[str]:
        return logistics_company_id

    @field_validator("truck_id")
    def validate_truck_id(cls, truck_id: str) -> Optional[str]:
        return truck_id
