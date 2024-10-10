from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from role_based_access_control import RoleBasedAccessControl
from models.clubs import ClubInternal
from models.user import UserInternal
from models.user.enums import UserRoles
from typing import Annotated
from ..models.update_club_model import UpdateClubRequest
from data.dbapis.clubs import find_club
from logging_config import log


class UpdateClubParameterControl:
    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(
                    RoleBasedAccessControl(
                        allowed_roles={UserRoles.ADMIN, UserRoles.CLUB}
                    )
                )
            ],
            update_club_request: UpdateClubRequest
    ):
        club = find_club(id=str(update_club_request.id))

        if user.user_role == UserRoles.CLUB:
            validation_result = self.validate_club_user_parameters(
                update_club_request=update_club_request,
                club=club,
                user_id=str(user.id)
            )

            if not validation_result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="club user is trying to update unauthorized fields"
                )

        self.user = user
        self.update_club_request = update_club_request


    @staticmethod
    def validate_club_user_parameters(
            update_club_request: UpdateClubRequest,
            club: ClubInternal,
            user_id: str
    ) -> bool:

        log.info("inside validate_club_user_parameters("
                 f"update_club_request={update_club_request},"
                 f"club={club},"
                 f"user_id={user_id})")

        club_user_ids = [user.user_id for user in club.users]
        does_user_belong_to_club =  user_id in club_user_ids

        if not does_user_belong_to_club:
            log.info("user does not belong to club, returning False")
            return False

        set_fields = update_club_request.model_dump(exclude_unset=True).keys()

        if "verification_status" in set_fields:
            log.info("club user is trying to update verification_status, returning False")
            return False

        return True







