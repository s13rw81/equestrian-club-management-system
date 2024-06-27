from typing import Annotated, Optional, List

from api.clubs.models.update_club_model import UpdateClubRequest
from data.dbapis.clubs.delete_queries import delete_club_by_id_logic
from data.dbapis.clubs.read_queries import get_all_clubs_logic, get_club_by_id_logic
from data.dbapis.clubs.update_queries import update_club_by_id_logic
from fastapi import APIRouter, Depends, HTTPException
from fastapi import status
from logging_config import log
from logic.auth import get_current_user
from models.clubs import ClubExternal
from models.clubs import ClubInternal
from models.user import UserInternal
from models.user.user_external import UserExternal

clubs_api_router = APIRouter(
    prefix = "/clubs",
    tags = ["clubs"]
)


@clubs_api_router.get("/")
async def get_all_clubs(user: Annotated[UserInternal, Depends(get_current_user)]) -> Optional[List[ClubExternal]]:
    # TODO: [phase ii] pagination
    # TODO: [phase ii] add filtering
    user_ext = UserExternal(**user.model_dump())
    log.info(f"getting list of clubs, user: {user} this is {__name__} module")
    result = get_all_clubs_logic()
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

    club = get_club_by_id_logic(club_id)

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

    existing_club = get_club_by_id_logic(club_id)
    if not existing_club:
        raise HTTPException(status_code = 404, detail = "Club not found")

    # TODO: add check to allow only admins to update club details
    # if existing_club.created_by.email_address != user.email_address:
    #     raise HTTPException(status_code = 403, detail = "User does not have permission to update this club")

    updated_club_details = ClubInternal(
        name = update_club.name if update_club.name else existing_club.name,
        description = update_club.description if update_club.description else existing_club.description,
        price = update_club.price if update_club.price else existing_club.price,
        image_urls = update_club.image_urls if update_club.image_urls else existing_club.image_urls,
        address = update_club.address if update_club.address else existing_club.address,
        contact = update_club.contact if update_club.contact else existing_club.contact,
        admins = update_club.admins if update_club.admins else existing_club.admins
    )
    result = update_club_by_id_logic(club_id = club_id, updated_club = updated_club_details)

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
    club = get_club_by_id_logic(club_id)
    if not club:
        emsg = f'club with id {club_id} not found.'
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = emsg
        )
    for admin in club.admins:
        if user.id == admin.id:
            # Delete the club
            result = delete_club_by_id_logic(club_id = club_id)
            msg = f"club deleted with id: {club_id} by user: {user_ext}"
            return {'status_code': 200, 'details': msg, 'data': result}

    return {'status_code': 403, 'detail': 'User does not have permission to delete this club'}