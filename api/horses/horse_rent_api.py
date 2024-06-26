from fastapi import HTTPException, APIRouter, status
from typing import List
from models.horse.horse_internal import InternalSellHorse, UploadedBy

from models.horse.horse_renting_service_internal import (
    HorseRentingServiceInternal, Provider
)
from .models.create_horse import HorseSellCreate
from data.dbapis.horses.horse_renting_service_queries import create_horse_renting_service

from data.dbapis.horses.horses_write_queries import create_horse

horse_rent_api_router = APIRouter(
    prefix="/user/horses/enlist-for-rent",
    tags=["rent_horses"]
)

@horse_rent_api_router.post("/", response_model=InternalSellHorse, status_code=201)
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
    )

    result = create_horse(new_horse)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Could not save the horse in the database"
        )
    new_horse.id = result

    new_horse_selling_service = HorseRentingServiceInternal(
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
    create_horse_renting_service(new_horse_selling_service)
    return new_horse

