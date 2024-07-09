from pydantic import BaseModel


class EnlistHorseForRent(BaseModel):
    name: str
    year_of_birth: str
    breed: str
    size: str
    gender: str
    description: str
    price: str


class EnlistHorseForRentResponse(BaseModel):
    horse_renting_service_id: str
