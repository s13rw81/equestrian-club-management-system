from fastapi import Depends, status
from fastapi.exceptions import HTTPException
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl
from ..models import UpdateTrainerDTO
from data.dbapis.trainers import find_trainer
from logging_config import log
from typing import Annotated

class UpdateTrainerParameterControl:
    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(
                    RoleBasedAccessControl(
                        allowed_roles={UserRoles.ADMIN, UserRoles.TRAINER}
                    )
                )
            ],
            update_trainer_dto: UpdateTrainerDTO
    ):
        log.info("inside UpdateTrainerParameterControl, validating access control policies..."
                 f"update_trainer_dto={update_trainer_dto}, user={user}")

        if user.user_role == UserRoles.TRAINER:
            trainer = find_trainer(user_id=str(user.id))

            if trainer.id != update_trainer_dto.id:
                log.info("the user is trying to update an entity that is not associated with him, "
                         "raising Exception...")

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="the user is trying to update an entity that is not associated with him"
                )

        self.user = user
        self.update_trainer_dto = update_trainer_dto

