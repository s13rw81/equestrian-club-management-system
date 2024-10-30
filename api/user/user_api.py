from fastapi import APIRouter, Depends, status, Request, UploadFile
from fastapi.exceptions import HTTPException

from data.db import get_countries_collection
from logging_config import log
from typing import Annotated
from .models import SignUpUser, ResponseUser, UpdateUser
from models.user import UserInternal, UpdateUserInternal
from data.dbapis.user.write_queries import save_user, update_user as update_user_db
from logic.auth import generate_password_hash, get_current_user, verify_sign_up_otp
from logic.user import upload_image_user_logic, upload_cover_image_user_logic
from utils.image_management import generate_image_url
from models.http_responses import Success
from datetime import datetime
import pytz

user_api_router = APIRouter(
    prefix="/user",
    tags=["users"]
)


@user_api_router.post("/signup")
async def signup(request: Request, sign_up_user: SignUpUser):
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
        gender=sign_up_user.gender,
        riding_stage=sign_up_user.riding_stage,
        horse_ownership_status=sign_up_user.horse_ownership_status,
        equestrian_discipline=sign_up_user.equestrian_discipline,
        user_category=sign_up_user.user_category,
        country=sign_up_user.country
    )

    result = save_user(user=user)

    if not result:
        log.info("could not save the user in the database, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not save the user in the database"
        )

    retval = Success(
        message="user created successfully...",
        data=ResponseUser(
            image=generate_image_url(image_id=user.image, request=request),
            cover_image=generate_image_url(image_id=user.cover_image, request=request),
            **user.model_dump(exclude={"image", "cover_image"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@user_api_router.get("/me")
async def me(request: Request, user: Annotated[UserInternal, Depends(get_current_user)]):
    log.info(f"user/me invoked (user_id={user.id})")

    response_user = ResponseUser(
        cover_image=generate_image_url(image_id=user.cover_image, request=request),
        **user.model_dump(exclude={"image", "cover_image"})
    )

    retval = Success(
        message="user fetched successfully",
        data=response_user
    )

    log.info(f"returning {retval}")

    return retval


@user_api_router.put("/update")
async def update_user_api(
        request: Request,
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

    retval = Success(
        message="user has been successfully updated...",
        data=ResponseUser(
            image=generate_image_url(image_id=user.image, request=request),
            cover_image=generate_image_url(image_id=user.cover_image, request=request),
            **user.model_dump(exclude={"image", "cover_image"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@user_api_router.post("/upload-image")
async def upload_image(
        request: Request,
        image: UploadFile,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /user/upload-image (user_id={user.id}, image_filename={image.filename})")

    user = await upload_image_user_logic(
        user_id=str(user.id),
        image=image
    )

    retval = Success(
        message="image uploaded successfully...",
        data=ResponseUser(
            cover_image=generate_image_url(image_id=user.cover_image, request=request),
            **user.model_dump(exclude={"image", "cover_image"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@user_api_router.post("/upload-cover-image")
async def upload_cover_image(
        request: Request,
        cover_image: UploadFile,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /user/upload-cover-image (user_id={user.id}, cover_image_filename={cover_image.filename})")

    user = await upload_cover_image_user_logic(
        user_id=str(user.id),
        cover_image=cover_image
    )

    retval = Success(
        message="cover image uploaded successfully...",
        data=ResponseUser(
            image=generate_image_url(image_id=user.image, request=request),
            cover_image=generate_image_url(image_id=user.cover_image, request=request),
            **user.model_dump(exclude={"image", "cover_image"})
        )
    )
