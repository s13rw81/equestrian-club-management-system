from fastapi import APIRouter, Depends
from .role_based_parameter_control.update_club_parameter_control import UpdateClubParameterControl
from typing import Annotated
from logging_config import log
from data.dbapis.clubs import find_club, update_club as update_club_db, find_club_by_user
from models.clubs import UpdateClubInternal
from models.user import UserInternal
from logic.auth import get_current_user
from models.http_responses import Success
from .models import GetClub
from datetime import datetime
import pytz

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

    existing_club = find_club(id=update_club_request.id.hex)

    # TODO: add last_updated_by id here after refactoring the user module to use uuid type id
    update_club_data = UpdateClubInternal(
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
        club_id: str,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /get-club/{club_id} (club_id={club_id}, user_id={user.id})")

    club = find_club(id=club_id)

    retval = Success(
        message="club retrieved successfully...",
        data=GetClub(**club.model_dump())
    ) if club else Success(
        message="no club exists with the provided id"
    )

    log.info(f"returning {retval}")

    return retval


@clubs_api_router.get("/get-your-club")
async def get_club_by_id(
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /get-your-club (user_id={user.id})")

    club = find_club_by_user(user_id=user.id)

    retval = Success(
        message="club retrieved successfully...",
        data=GetClub(**club.model_dump())
    ) if club else Success(
        message="no club exists with the provided id"
    )

    log.info(f"returning {retval}")

    return retval