from fastapi import APIRouter, Depends, Request, HTTPException, status, UploadFile
from .role_based_parameter_control.update_club_parameter_control import UpdateClubParameterControl
from .role_based_parameter_control.upload_images_parameter_control import UploadImagesParameterControl
from typing import Annotated
from logging_config import log
from data.dbapis.clubs import find_club, update_club as update_club_db, find_club_by_user
from models.clubs import UpdateClubInternal
from models.user import UserInternal
from logic.auth import get_current_user
from logic.clubs import upload_logo_logic, upload_images_logic
from models.http_responses import Success
from .models import GetClub
from datetime import datetime
import pytz
from utils.image_management import generate_image_urls, generate_image_url
from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles

clubs_api_router = APIRouter(
    prefix="/clubs",
    tags=["clubs"]
)


@clubs_api_router.put("/update-club")
async def update_club(
        update_club_parameter_control: Annotated[
            UpdateClubParameterControl,
            Depends()
        ]
):
    update_club_request = update_club_parameter_control.update_club_request
    user = update_club_parameter_control.user

    log.info(
        f"inside /clubs/update-club ("
        f"update_club_request={update_club_request}, "
        f"user={user})"
    )

    existing_club = find_club(id=str(update_club_request.id))

    # TODO: add last_updated_by id here after refactoring the user module to use uuid type id
    update_club_data = UpdateClubInternal(
        last_updated_by=user.id,
        last_updated_on=datetime.now(pytz.utc),
        **update_club_request.model_dump(exclude_unset=True)
    )

    if update_club_request.club_id:
        log.info("club_id is provided in the update_data, creating new platform_id")
        platform_id_elements = existing_club.platform_id.split("_")
        new_platform_id = f"{platform_id_elements[0]}_{update_club_request.club_id}_{platform_id_elements[2]}"
        log.info(f"new platform_id={new_platform_id}")
        update_club_data.platform_id = new_platform_id

    updated_club = update_club_db(update_club_data=update_club_data)

    log.info("club updated successfully, returning...")

    return Success(
        message="club updated successfully...",
        data={
            "updated_club": GetClub(**updated_club.model_dump())
        }
    )


@clubs_api_router.get("/get-club/{club_id}")
async def get_club_by_id(
        request: Request,
        club_id: str,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /clubs/get-club/{club_id} (club_id={club_id}, user_id={user.id})")

    club = find_club(id=club_id)

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no club exists with the provided id (club_id={club_id})"
        )

    retval = Success(
        message="club retrieved successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-your-club")
async def get_your_club(
        request: Request,
        user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.CLUB}))
        ]
):
    log.info(f"inside /clubs/get-your-club (user_id={user.id})")

    club = find_club_by_user(user_id=user.id)

    if not club:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no club is associated with the user"
        )

    retval = Success(
        message="club retrieved successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-logo")
async def upload_logo(
        request: Request,
        logo: UploadFile,
        upload_images_parameter_control: Annotated[
            UploadImagesParameterControl,
            Depends()
        ]
):
    user = upload_images_parameter_control.user
    club_id = upload_images_parameter_control.club_id

    log.info(f"inside /clubs/upload-logo(user_id={user.id}, club_id={club_id})")

    club = await upload_logo_logic(
        club_id=club_id,
        logo=logo
    )

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.post("/upload-images")
async def upload_logo(
        request: Request,
        images: list[UploadFile],
        upload_images_parameter_control: Annotated[
            UploadImagesParameterControl,
            Depends()
        ]
):
    user = upload_images_parameter_control.user
    club_id = upload_images_parameter_control.club_id

    log.info(f"inside /clubs/upload-images(user_id={user.id}, club_id={club_id})")

    club = await upload_images_logic(
        club_id=club_id,
        images=images
    )

    retval = Success(
        message="logo uploaded successfully...",
        data=GetClub(
            logo=generate_image_url(image_id=club.logo, request=request),
            images=generate_image_urls(image_ids=club.images, request=request),
            **club.model_dump(exclude={"logo", "images"})
        )
    )

    log.info(f"returning {retval}")

    return retval
