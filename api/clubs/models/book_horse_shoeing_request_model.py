# {
#   "trainer_id": "the chosen id of the trainer",
#   "date": "the chosen date",
#   "pricing_option": "the chosen pricing option",
#   "number_of_visitors": "number of visitors that are coming"
# }
from datetime import datetime, timezone

from data.dbapis.trainer.read_queries import get_trainer_by_trainer_id
from pydantic import BaseModel, field_validator
from utils.date_time import get_current_utc_datetime


class HorseShoeingBookingRequest(BaseModel):
    trainer_id: str
    selected_date: datetime
    pricing_option: dict
    number_of_visitors: int

    @field_validator('trainer_id')
    def validate_trainer_id(cls, trainer_id):
        trainer = get_trainer_by_trainer_id(trainer_id)
        if not trainer:
            raise ValueError('invalid trainer_id.')
        return trainer_id

    @field_validator('selected_date')
    def validate_date(cls, date):
        if date < get_current_utc_datetime():
            raise ValueError('The date must not be from the past.')
        return date
