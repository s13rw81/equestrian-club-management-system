from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
from logging_config import log
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from logic.auth import get_current_user
from models.horse.horse_internal import InternalSellHorse, UploadedBy
from models.horse.horse_update_internal import InternalUpdateSellHorse
from models.horse.horse_selling_service_internal import HorseSellingServiceInternal, Provider
from .models.create_horse import HorseCreate, HorseSaleResponse
from .models.update_horse import HorseSellUpdate
from data.dbapis.horses.horse_selling_service_queries import create_horse_selling_service, update_horse_selling_service, get_horse_selling_service
from data.dbapis.horses.horses_read_queries import get_all_horses, get_horse_by_id
from data.dbapis.horses.horses_write_queries import create_horse, update_horse, delete_horse
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from role_based_access_control import RoleBasedAccessControl

horse_sell_api_router = APIRouter(
    prefix="/user/horses/enlist-for-sell",
    tags=["sell_horses"]
)

@horse_sell_api_router.post("/", response_model=HorseSaleResponse, status_code=201)
async def create_horse_endpoint(
    horse: HorseCreate,
    user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.ADMIN, UserRoles.USER, UserRoles.CLUB})),
        ]):
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

    new_horse_selling_service = HorseSellingServiceInternal(
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
    selling_service_id = create_horse_selling_service(new_horse_selling_service)

    return HorseSaleResponse(
        horse_id=new_horse.id,
        horse_selling_service_id=selling_service_id
    )


@horse_sell_api_router.put("/update-sell-listing/{horse_selling_service_id}")
async def update_sell_listing(
    horse_selling_service_id: str,
    horse: HorseSellUpdate,
    user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.ADMIN, UserRoles.USER, UserRoles.CLUB})),
        ]
):
    horse_selling_service = get_horse_selling_service(horse_selling_service_id)
    if not horse_selling_service:
        raise HTTPException(status_code=404, detail="Horse selling service not found")
    if horse_selling_service["provider"]["provider_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this listing")

    horse_id = horse_selling_service["horse_id"]
    update_data = jsonable_encoder(horse, exclude_unset=True)

    updated_horse = update_horse(horse_id, update_data)
    if not updated_horse:
        raise HTTPException(status_code=404, detail="Horse not found")

    updated_service = update_horse_selling_service(horse_selling_service_id, update_data)
    if not updated_service:
        raise HTTPException(status_code=500, detail="Failed to update horse selling service")

    return {"status": "OK"}
