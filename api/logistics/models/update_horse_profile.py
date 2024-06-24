from pydantic import BaseModel


class HorseProfile(BaseModel):
    horse_name: str
    age: int
    health_info: str
    customer_transfer_id: str


class ResponseHorseProfile(BaseModel):
    profile_id: str
