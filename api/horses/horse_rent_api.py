from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional
from .models.rent_horse import ResponseModel
from models.horse.horse_rent_internal import Horse
from data.dbapis.horses.horse_renting_queries import search_horses_for_rent, contact_owner


horse_rent_router = APIRouter(
    prefix="/horses",
    tags=["horses"]
)
@horse_rent_router.get("/rent", response_model=List[Horse])
def get_horses_for_rent(
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    date: Optional[str] = None,
    duration: Optional[str] = None,
):
    return search_horses_for_rent(search, min_price, max_price, date, duration)

@horse_rent_router.post("/{id}/contact", response_model=ResponseModel)
def post_contact_owner(
    id: str,
    date: str,
    duration: str,
    Authorization: str = Header(None),
):
    # if not Authorization:
    #     raise HTTPException(status_code=401, detail="Authorization header missing")

    result = contact_owner(id, date, duration)
    if result["success"]:
        return result
    else:
        raise HTTPException(status_code=404 if result["message"] == "Horse not found" else 500, detail=result["message"])
