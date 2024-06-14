from fastapi import HTTPException, APIRouter
from typing import List
from api.horses.models.horse_data_models import Horse
from data.dbapis.horses.crud import (
    get_all_horses, get_horse_by_id,
    create_horse, update_horse, delete_horse
)

horse_api_router = APIRouter(
    prefix="/horses",
    tags=["horses"]
)


@horse_api_router.get("/", response_model=List[Horse])
async def read_horses():
    horses = get_all_horses()
    return horses


@horse_api_router.get("/{horse_id}", response_model=Horse)
async def read_horse(horse_id: str):
    horse = get_horse_by_id(horse_id)
    if horse:
        return horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_api_router.post("/", response_model=Horse, status_code=201)
async def create_horse_endpoint(horse: Horse):
    new_horse = create_horse(horse)
    return new_horse


@horse_api_router.put("/{horse_id}", response_model=Horse)
async def update_horse_endpoint(horse_id: str, horse: Horse):
    updated_horse = update_horse(horse_id, horse)
    if updated_horse:
        return updated_horse
    raise HTTPException(status_code=404, detail="Horse not found")


@horse_api_router.delete("/{horse_id}", status_code=204)
async def delete_horse_endpoint(horse_id: str):
    if delete_horse(horse_id):
        return
    raise HTTPException(status_code=404, detail="Horse not found")
