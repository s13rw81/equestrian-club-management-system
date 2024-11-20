from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles
from models.user import UserInternal
from ..models import GenerateTrainerAffiliationDTO
from typing import Annotated
from data.dbapis.clubs import find_club_by_user
from logging_config import log



class GenerateTrainerAffiliationParamControl:
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
            generate_trainer_affiliation_dto: GenerateTrainerAffiliationDTO
    ):
        if user.user_role == UserRoles.CLUB:
            club = find_club_by_user(user_id=str(user.id))

            if str(club.id) != generate_trainer_affiliation_dto.club_id:
                log.info("user is trying to create generate trainer affiliation "
                         "for a club that he does not have access to... "
                         "raising HTTPException")

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="club user is trying to generate affiliation number for other clubs"
                )

        self.user = user
        self.generate_trainer_affiliation_dto = generate_trainer_affiliation_dto
