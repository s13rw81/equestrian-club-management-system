from fastapi import HTTPException, APIRouter, status
from typing import List
from models.horse.horse_internal import InternalHorse
from models.horse.horse_update_internal import InternalUpdateHorse
from .models.create_horse import HorseCreate
from .models.update_horse import HorseUpdate
from data.dbapis.horses.horses_read_data import (
    get_all_horses, get_horse_by_id,
)

from data.dbapis.horses.horses_write_data import (
    create_horse, update_horse, delete_horse
)

horse_api_router = APIRouter(
    prefix="/horses",
    tags=["horses"]
)


@horse_api_router.get("/", response_model=List[InternalHorse])
async def read_horses():
    horses = get_all_horses()
    return horses


@horse_api_router.get("/{horse_id}", response_model=InternalHorse)
async def read_horse(horse_id: str):
    horse = get_horse_by_id(horse_id)
    if horse:
        return horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_api_router.post("/", response_model=InternalHorse, status_code=201)
async def create_horse_endpoint(horse: HorseCreate):
    new_horse = InternalHorse(
        name=horse.name,
        description=horse.description,
        year=horse.year,
        height_cm=horse.height_cm,
        club_name=horse.club_name,
        price_sar=horse.price_sar,
        image_url=horse.image_url,
        contact_seller_url=horse.contact_seller_url,
        go_transport_url=horse.go_transport_url
    )

    result = create_horse(new_horse)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the horse in the database"
        )
    new_horse.id = result  # Assign the ID to the horse instance
    return new_horse


@horse_api_router.put("/{horse_id}", response_model=InternalUpdateHorse)
async def update_horse_endpoint(horse_id: str, horse: HorseUpdate):
    updated_horse = update_horse(horse_id, horse.dict(exclude_unset=True))
    if updated_horse:
        return updated_horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_api_router.delete("/{horse_id}", status_code=204)
async def delete_horse_endpoint(horse_id: str):
    if delete_horse(horse_id):
        return {"Message": "Deleted Sucessfully"}
    raise HTTPException(status_code=404, detail="Horse not found")
