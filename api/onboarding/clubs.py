from typing import Annotated
from api.onboarding.models import CreateTrainerDTO
from api.onboarding.onboarding_router import onboarding_api_router
from data.dbapis.clubs import get_club_count
from fastapi import Depends
from logging_config import log
from logic.onboarding.clubs import create_club as create_club_logic
from models.user import UserInternal, UserRoles
from models.clubs import ClubInternal, ClubUser
from role_based_access_control import RoleBasedAccessControl
from models.http_responses import Success


@onboarding_api_router.post("/create-club")
async def create_club(
        create_club_request: CreateTrainerDTO,
        user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]
):
    """
    :param user: user invoking the api
    :param create_club_request: instance of CreateClub dto
    :return: instance of str, id of new club created
    """
    log.info(f"/create-club invoked (create_club_request={create_club_request}, user_id={user.id})")

    existing_club_count = get_club_count()

    club = ClubInternal(
        created_by=user.id,
        users=[
            ClubUser(user_id=user.id)
        ],
        platform_id=f"khayyal_{create_club_request.club_id}_{existing_club_count + 1}",
        **create_club_request.model_dump()
    )

    newly_created_club = create_club_logic(club=club, user=user)

    return Success(
        message="club created successfully",
        data={
            "id": str(newly_created_club.id)
        }
    )
