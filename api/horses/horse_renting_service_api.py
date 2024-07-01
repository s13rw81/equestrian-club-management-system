from fastapi import HTTPException, APIRouter, status, Depends
from typing import List
from .models.horse_renting_service import HorseRentingItem
from data.dbapis.horses.horse_renting_service_queries import get_renting_horse_by_id
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.horse.horse_internal import InternalSellHorse
from logic.auth import get_current_user
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

horse_renting_service_api_router = APIRouter(
    prefix="/user/horses/get-horses-for-rent",
    tags=["horses_renting_services"]
)

@horse_renting_service_api_router.get("/{horse_id}", response_model=List[InternalSellHorse])
async def get_horses_renting(
    horse_id: str,
    user: UserInternal = Depends(RoleBasedAccessControl({UserRoles.ADMIN, UserRoles.USER})),
):
    horse = get_renting_horse_by_id(horse_id)
    if horse:
        return JSONResponse(content=jsonable_encoder([horse]))
    raise HTTPException(status_code=404, detail="Horse not found")