from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from logging_config import log
from typing import Annotated
from .models import SignUpUser, ResponseUser, UpdateUser
from models.user import UserInternal, UpdateUserInternal
from data.dbapis.user.write_queries import save_user, update_user as update_user_db
from logic.auth import generate_password_hash, get_current_user

user_api_router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@user_api_router.post("/signup")
async def signup(sign_up_user: SignUpUser):
    log.info(f"/signup invoked: sign_up_user = {sign_up_user}")

    user = UserInternal(
        full_name=sign_up_user.full_name,
        email_address=sign_up_user.email_address,
        phone_number=sign_up_user.phone_number,
        hashed_password=generate_password_hash(sign_up_user.password),
        riding_stage=sign_up_user.riding_stage,
        horse_ownership_status=sign_up_user.horse_ownership_status,
        equestrian_discipline=sign_up_user.equestrian_discipline
    )

    result = save_user(user=user)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the user in the database"
        )

    return {"id": result}


@user_api_router.get("/me")
async def me(user: Annotated[UserInternal, Depends(get_current_user)]) -> ResponseUser:
    log.info(f"/me invoked")

    response_user = ResponseUser(**user.model_dump())

    log.info(f"returning {response_user}")

    return response_user
