from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from logging_config import log
from logic.auth import get_current_user
from models.horse.horse_internal import InternalSellHorse, UploadedBy
from models.horse.horse_renting_service_internal import HorseRentingServiceInternal, Provider
from .models.create_horse import HorseCreate, HorseRentResponse
from data.dbapis.horses.horse_renting_service_queries import create_horse_renting_service
from data.dbapis.horses.horses_write_queries import create_horse
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from role_based_access_control import RoleBasedAccessControl

horse_rent_api_router = APIRouter(
    prefix="/user/horses/enlist-for-rent",
    tags=["rent_horses"]
)

@horse_rent_api_router.post("/", response_model=HorseRentResponse, status_code=201)
async def create_horse_endpoint(
    horse: HorseCreate,
    user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.ADMIN}))]
):
    user_ext = UserExternal(**user.model_dump())
    log.info(f"Creating a horse listing, user: {user_ext}")

    # Ensure uploaded_by is an instance of UploadedBy
    uploaded_by_instance = UploadedBy(
        uploaded_by_id=user.id,  # Using user ID directly from the authenticated user
        uploaded_by_type=user.user_role.value  # Using user role directly from the authenticated user
    )

    new_horse = InternalSellHorse(
        name=horse.name,
        year_of_birth=horse.year_of_birth,
        breed=horse.breed,
        size=horse.size,
        gender=horse.gender,
        description=horse.description,
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
        provider=Provider(
            provider_id=user.id,
            provider_type=new_horse.uploaded_by.uploaded_by_type
        ),
        price_sar=horse.price_sar
    )
    create_horse_renting_service(new_horse_selling_service)

    return HorseRentResponse(
        horse_renting_service_id=new_horse.id
    )
