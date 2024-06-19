from fastapi import HTTPException, APIRouter, status
from typing import List
from models.horse.horse_sell_internal import InternalSellHorse
from models.horse.horse_update_sell_internal import InternalUpdateSellHorse
from .models.create_sale_horse import HorseSellCreate
from .models.update_sale_horse import HorseSellUpdate
from data.dbapis.horses.horses_sell_read_queries import (
    get_all_horses, get_horse_by_id,
)

from data.dbapis.horses.horses_sell_write_queries import (
    create_horse, update_horse, delete_horse
)

horse_sell_api_router = APIRouter(
    prefix="/api/v1/horses",
    tags=["sell_horses"]
)


@horse_sell_api_router.get("/sell", response_model=List[InternalSellHorse])
async def read_horses():
    horses = get_all_horses()
    return horses


@horse_sell_api_router.get("/sell/{horse_id}", response_model=InternalSellHorse)
async def read_horse(horse_id: str):
    horse = get_horse_by_id(horse_id)
    if horse:
        return horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_sell_api_router.post("/sell", response_model=InternalSellHorse, status_code=201)
async def create_horse_endpoint(horse: HorseSellCreate):
    new_horse = InternalSellHorse(
        name=horse.name,
        type=horse.type,
        description=horse.description,
        year=horse.year,
        height_cm=horse.height_cm,
        club_name=horse.club_name,
        price_sar=horse.price_sar,
        image_url=horse.image_url,
    )

    result = create_horse(new_horse)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the horse in the database"
        )
    new_horse.id = result  # Assign the ID to the horse instance
    return new_horse


@horse_sell_api_router.put("/sell/{horse_id}",
                           response_model=InternalUpdateSellHorse)
async def update_horse_endpoint(horse_id: str, horse: HorseSellUpdate):
    updated_horse = update_horse(horse_id, horse.dict(exclude_unset=True))
    if updated_horse:
        return updated_horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_sell_api_router.delete("/sell/{horse_id}", status_code=204)
async def delete_horse_endpoint(horse_id: str):
    if delete_horse(horse_id):
        return {"Message": "Deleted Sucessfully"}
    raise HTTPException(status_code=404, detail="Horse not found")
