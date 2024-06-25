from typing import Annotated

from api.clubs import CreateClubRequest
from data.dbapis.clubs import save_club
from fastapi import Depends
from logging_config import log
from logic.auth import get_current_user
from models.clubs import ClubInternal
from models.user import UserInternal
from models.user.user_external import UserExternal
from api.onboarding.onboarding_router import onboarding_api_router


@onboarding_api_router.post("/club")
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
    # Convert the request model to the DB model
    new_club_internal = ClubInternal(**create_new_club.dict(), admins = [user_ext])
    result = save_club(new_club_internal)
    msg = f"new club created with id: {result} by user: {user_ext}"
    return {'status_code': 201, 'details': msg, 'data': result}

