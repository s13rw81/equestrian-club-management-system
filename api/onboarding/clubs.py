from typing import Annotated
from data.dbapis.clubs import get_club_count
from fastapi import Depends
from logging_config import log
from logic.onboarding.clubs import create_club as create_club_logic
from models.user import UserInternal
from models.user.enums import UserRoles
from models.clubs import ClubInternal, ClubUser
from models.http_responses import Success
from .models import CreateClubRequest
from role_based_access_control import RoleBasedAccessControl
from . import onboarding_api_router

@onboarding_api_router.post("/create-club")
async def create_club(
        create_club_request: CreateClubRequest,
        user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]
):
    log.info(f"/create-club invoked (create_club_request={create_club_request}, user_id={user.id})")

    existing_club_count = get_club_count()

    club = ClubInternal(
        created_by=user.id,
        users=[
            ClubUser(user_id=str(user.id))
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
