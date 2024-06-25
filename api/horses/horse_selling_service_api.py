from fastapi import HTTPException, APIRouter, status
from typing import List
from .models.horse_selling_service import HorseSellingItem
from data.dbapis.horses.horse_selling_service_queries import get_horse_by_id
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

horse_selling_service_api_router = APIRouter(
    prefix="/user/horses/get-horses-for-sale",
    tags=["horses_selling_services"]
)

@horse_selling_service_api_router.get("/{horse_id}", response_model=List[HorseSellingItem])
async def get_horses_selling(horse_id: str):
    horse = get_horse_by_id(horse_id)
    if horse:
        return JSONResponse(content=jsonable_encoder([horse]))  # Return a list containing the horse
    raise HTTPException(status_code=404, detail="Horse not found")
