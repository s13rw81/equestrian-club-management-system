from typing import Annotated, Optional, List

from api.clubs.models import CreateClubRequest
from api.clubs.models.delete_club_model import DeleteClubRequest
from api.clubs.models.update_club_model import UpdateClubRequest
from data.dbapis.clubs.delete_queries import async_delete_club_by_id
from data.dbapis.clubs.read_queries import async_get_clubs, async_get_club_by_id
from data.dbapis.clubs.update_queries import async_update_club_by_id
from data.dbapis.clubs.write_queries import async_save_club
from fastapi import APIRouter, Depends, HTTPException
from logging_config import log
from logic.auth import get_current_user
from models.clubs.clubs_external import ClubExternal
from models.clubs.clubs_internal import ClubInternal
from models.user import UserInternal
from models.user.user_external import UserExternal
from fastapi import status
from utils.date_time import get_current_utc_datetime

clubs_api_router = APIRouter(
    prefix = "/clubs",
    tags = ["clubs"]
)


@clubs_api_router.post("/onboard")
async def create_club(create_new_club: CreateClubRequest,
                      user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    """
    :param user: user invoking the api
    :param create_new_club: instace of CreateClub dto
    :return: instance of str, id of new club created
    """
    # TODO: [phase ii] check if user has permission to add club
    log.info(f"creating club, user: {user}")
    user_ext = UserExternal(**user.model_dump())
    utc_date_time = get_current_utc_datetime()
    # Convert the request model to the DB model
    new_club_internal = ClubInternal(**create_new_club.dict(), creation_date_time = utc_date_time,
                                     update_date_time = utc_date_time, admins = [user_ext])
    result = await async_save_club(new_club_internal)
    msg = f"new club created with id: {result} by user: {user_ext}"
    return {'status_code': 201, 'details': msg, 'data': result}


@clubs_api_router.get("/")
async def get_all_clubs(user: Annotated[UserInternal, Depends(get_current_user)]) -> Optional[List[ClubExternal]]:
    # TODO: [phase ii] pagination
    # TODO: [phase ii] add filtering
    user_ext = UserExternal(**user.model_dump())
    log.info(f"getting list of clubs, user: {user} this is {__name__} module")
    result = await async_get_clubs()
    log.info(f"result {result}, user: {user_ext}")
    return result


@clubs_api_router.get("/{club_id}")
async def get_club_by_id(user: Annotated[UserInternal, Depends(get_current_user)], club_id: str) -> ClubExternal | None:
    """
    :param user:
    :param club_id: id of the club to be fetched
    :return: instance of ClubInternal, details of the club
    """
    user_ext = UserExternal(**user.model_dump())
    log.info(f"fetching club with id: {club_id}, user is {user_ext}")

    club = await async_get_club_by_id(club_id)

    if not club:
        raise HTTPException(status_code = 404, detail = "Club not found")

    log.info(f"club fetched with id: {club_id} by user {user_ext}")
    return club


@clubs_api_router.put("/{club_id}")
async def update_club_by_id(club_id: str, user: Annotated[UserExternal, Depends(get_current_user)],
                            update_club: UpdateClubRequest) -> dict[str, str | int]:
    """
    :param club_id: id of the club to be updated
    :param user: user invoking the api
    :param update_club: instance of UpdateClub dto
    :return: instance of str, id of updated club
    """

    # TODO: check if user has permission to update club
    # TODO: add apis to delete club images
    user_ext = UserExternal(**user.model_dump())
    log.info(f"updating club with id: {club_id}, user: {user_ext}")

    existing_club = await async_get_club_by_id(club_id)
    if not existing_club:
        raise HTTPException(status_code = 404, detail = "Club not found")

    #TODO: add check to allow only admins to update club details
    # if existing_club.created_by.email_address != user.email_address:
    #     raise HTTPException(status_code = 403, detail = "User does not have permission to update this club")

    utc_date_time = get_current_utc_datetime()

    updated_club_details = ClubInternal(
        name = update_club.name if update_club.name else existing_club.name,
        description = update_club.description if update_club.description else existing_club.description,
        price = update_club.price if update_club.price else existing_club.price,
        update_date_time = utc_date_time,
        image_urls = update_club.image_urls if update_club.image_urls else existing_club.image_urls,
    )
    result = await async_update_club_by_id(club_id=club_id, updated_club = updated_club_details)

    if not result:
        raise HTTPException(status_code = 404, detail = "Club not found or not updated")

    msg = f"club with id: {club_id} updated by user: {user_ext}"
    log.info(msg)
    return {'status_code': 200, 'details': msg, 'data': result}


@clubs_api_router.delete("/{club_id}")
async def delete_club(club_id: str, user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    """
    :param club_id:
    :param user: user invoking the api
    :return: status message
    """
    user_ext = UserExternal(**user.model_dump())
    log.info(f"deleting club, user: {user}")
    # Check if the user is the creator of the club
    club = await async_get_club_by_id(club_id)
    if not club:
        emsg = f'club with id {club_id} not found.'
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = emsg
        )
    for admin in club.admins:
        if user.id == admin.id:
            # Delete the club
            result = await async_delete_club_by_id(club_id = club_id)
            msg = f"club deleted with id: {club_id} by user: {user_ext}"
            return {'status_code': 200, 'details': msg, 'data': result}

    return {'status_code': 403, 'detail': 'User does not have permission to delete this club'}

