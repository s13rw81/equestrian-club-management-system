from fastapi import HTTPException, APIRouter, status
from typing import List
from models.horse.horse_sell_internal import InternalSellHorse, UploadedBy
from models.horse.horse_update_sell_internal import InternalUpdateSellHorse
from models.horse.horse_selling_service_internal import (
    HorseSellingServiceInternal, Provider
)
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
    # Ensure uploaded_by is an instance of UploadedBy
    uploaded_by_instance = UploadedBy(
        uploaded_by_id=horse.uploaded_by.uploaded_by_id,
        uploaded_by_type=horse.uploaded_by.uploaded_by_type
    )

    new_horse = InternalSellHorse(
        name=horse.name,
        year_of_birth=horse.year_of_birth,
        breed=horse.breed,
        size=horse.size,
        gender=horse.gender,
        description=horse.description,
        images=horse.images,
        uploaded_by=uploaded_by_instance,
        price_sar=horse.price_sar
    )

    result = create_horse(new_horse)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the horse in the database"
        )
    new_horse.id = result

    new_horse_selling_service = HorseSellingServiceInternal(
        horse_id=new_horse.id,
        name=new_horse.name,
        year_of_birth=new_horse.year_of_birth,
        breed=new_horse.breed,
        size=new_horse.size,
        gender=new_horse.gender,
        description=new_horse.description,
        images=new_horse.images,
        provider=Provider(
            provider_id=new_horse.uploaded_by.uploaded_by_id,
            provider_type=new_horse.uploaded_by.uploaded_by_type
        ),
        price_sar=horse.price_sar
    )
    create_horse_selling_service(new_horse_selling_service)
    return new_horse
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
