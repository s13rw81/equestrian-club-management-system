from fastapi import HTTPException, APIRouter, status
from typing import List
from models.horse.horse_sell_internal import InternalSellHorse
from models.horse.horse_update_sell_internal import InternalUpdateSellHorse
from models.horse.horse_selling_service_internal import HorseSellingServiceInternal
from .models.create_sale_horse import HorseSellCreate
from .models.update_sale_horse import HorseSellUpdate
from data.dbapis.horses.horse_selling_service_queries import create_horse_selling_service
from data.dbapis.horses.horses_sell_read_queries import (
    get_all_horses, get_horse_by_id,
)

from data.dbapis.horses.horses_sell_write_queries import (
    create_horse, update_horse, delete_horse
)

horse_sell_api_router = APIRouter(
    prefix="/user/horses/enlist-for-sell",
    tags=["sell_horses"]
)


@horse_sell_api_router.get("/", response_model=List[InternalSellHorse])
async def read_horses():
    horses = get_all_horses()
    return horses


@horse_sell_api_router.get("/{horse_id}", response_model=InternalSellHorse)
async def read_horse(horse_id: str):
    horse = get_horse_by_id(horse_id)
    if horse:
        return horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_sell_api_router.post("/", response_model=InternalSellHorse, status_code=201)
async def create_horse_endpoint(horse: HorseSellCreate):
    new_horse = InternalSellHorse(
        name=horse.name,
        type=horse.type,
        description=horse.description,
        year=horse.year,
        height_cm=horse.height_cm,
        price_sar=horse.price_sar,
        image_url=horse.image_url,
        uploaded_by_id=horse.uploaded_by_id,
        uploaded_by_type=horse.uploaded_by_type
    )
    result = create_horse(new_horse)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the horse in the database"
        )
    new_horse.id = result  # Assign the ID to the horse instance


        # Create a record in the horse_sell_services collection
    new_horse_selling_service = HorseSellingServiceInternal(
        horse_id=new_horse.id,
        name=new_horse.name,
        type=new_horse.type,
        description=new_horse.description,
        year=new_horse.year,
        height_cm=new_horse.height_cm,
        price_sar=new_horse.price_sar,
        image_url=new_horse.image_url,
        uploaded_by_id=new_horse.uploaded_by_id,
        uploaded_by_type=new_horse.uploaded_by_type
    )
    service_result = create_horse_selling_service(new_horse_selling_service)
    if service_result:
        return new_horse
    raise HTTPException(status_code=500, detail="could not save the horse in the database")


@horse_sell_api_router.put("/{horse_id}",
                           response_model=InternalUpdateSellHorse)
async def update_horse_endpoint(horse_id: str, horse: HorseSellUpdate):
    updated_horse = update_horse(horse_id, horse.dict(exclude_unset=True))
    if updated_horse:
        return updated_horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_sell_api_router.delete("/{horse_id}", status_code=204)
async def delete_horse_endpoint(horse_id: str):
    if delete_horse(horse_id):
        return {"Message": "Deleted Sucessfully"}
    raise HTTPException(status_code=404, detail="Horse not found")
