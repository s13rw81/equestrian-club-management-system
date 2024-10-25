from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException

from data.db import get_countries_collection
from logging_config import log
from typing import Annotated
from .models import SignUpUser, ResponseUser, UpdateUser
from models.user import UserInternal, UpdateUserInternal
from data.dbapis.user.write_queries import save_user, update_user as update_user_db
from logic.auth import generate_password_hash, get_current_user, verify_sign_up_otp
from models.http_responses import Success
from datetime import datetime
import pytz

user_api_router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@user_api_router.post("/signup")
async def signup(sign_up_user: SignUpUser):
    log.info(f"/signup invoked: sign_up_user = {sign_up_user}")

    verification_result = verify_sign_up_otp(
        user_provided_otp=sign_up_user.phone_otp,
        phone_number=sign_up_user.phone_number
    )

    if not verification_result:
        log.info("OTP verification failed, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="invalid OTP, please try again..."
        )

    user = UserInternal(
        full_name=sign_up_user.full_name,
        email_address=sign_up_user.email_address,
        phone_number=sign_up_user.phone_number,
        hashed_password=generate_password_hash(sign_up_user.password),
        riding_stage=sign_up_user.riding_stage,
        horse_ownership_status=sign_up_user.horse_ownership_status,
        equestrian_discipline=sign_up_user.equestrian_discipline,
        user_category=sign_up_user.user_category
    )

    result = save_user(user=user)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the user in the database"
        )

    return Success(
        message="user created successfully...",
        data=ResponseUser(**result.model_dump())
    )


@user_api_router.get("/me")
async def me(user: Annotated[UserInternal, Depends(get_current_user)]):
    log.info(f"/me invoked")

    response_user = ResponseUser(**user.model_dump())

    log.info(f"returning {response_user}")

    return Success(
        message="user fetched successfully",
        data=response_user
    )


@user_api_router.put("/update")
async def update_user_api(
        update_user: UpdateUser,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"/user/update (update_user={update_user}, user={user})")

    update_user_dto = UpdateUserInternal(
        id=user.id,
        last_updated_on=datetime.now(pytz.utc),
        **update_user.model_dump(exclude_unset=True)
    )

    result = update_user_db(update_user_dto=update_user_dto)

    log.info(f"update completed, updated_user={result}")

    return Success(
        message="user has been successfully updated...",
        data=ResponseUser(**result.model_dump())
    )


"""__________________________________________________________________________________________________________________"""


# Fetch all countries API
@user_api_router.get("/countries")
async def get_all_countries():
    log.info("/countries invoked")

    countries = get_countries_collection()

    if not countries:
        log.info("No countries found in the database.")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No countries found"
        )

    log.info(f"Countries retrieved: {countries}")

    return Success(
        message="Countries fetched successfully.",
        data=countries
    )


"""__________________________________________________________________________________________________________________"""
