from typing import Annotated, Optional

from fastapi import Depends, Form, HTTPException, status

from data.dbapis.trainer_certifications import find_trainer_certification
from data.dbapis.trainers import find_trainer
from logging_config import log
from models.user import UserInternal
from models.user.enums import UserRoles
from role_based_access_control import RoleBasedAccessControl


class TrainerCertIdParamCtrlForm:
    def __init__(
        self,
        user: Annotated[
            UserInternal,
            Depends(
                RoleBasedAccessControl(
                    allowed_roles={UserRoles.TRAINER, UserRoles.ADMIN}
                )
            ),
        ],
        # trainer_certification_id: str = Form(..., description="the database uuid"),
        name: str = Form(..., description="the name of the certification"),
        number: str = Form(..., description="the number of the certification"),
        trainer_id: Optional[str] = Form(
            None,
            description="the id of the trainer for which to upload certification. Mandatory for Admin Role",
        ),
    ):
        log.info(f"inside __init__(user_id={user.id}, name={name}, number={number})")

        # trainer_certification = find_trainer_certification(id=trainer_certification_id)

        # if not trainer_certification:
        #     log.info("invalid trainer_certification_id, raising HTTPException...")
        #     raise HTTPException(
        #         status_code=status.HTTP_406_NOT_ACCEPTABLE,
        #         detail="invalid trainer_certification_id...",
        #     )

        if user.user_role == UserRoles.TRAINER:
            log.info("user role is trainer; validating with trainer_id...")
            trainer = find_trainer(user_id=str(user.id))

        #     if trainer_certification.trainer_id != str(trainer.id):
        #         log.info(
        #             "user is not authorized to modify this trainer certification..."
        #         )
        #         raise HTTPException(
        #             status_code=status.HTTP_401_UNAUTHORIZED,
        #             detail="user is not authorized to modify this trainer certification...",
        #         )

        self.user = user
        self.name = name
        self.number = number
        self.trainer_id = (
            str(trainer.id) if user.user_role == UserRoles.TRAINER else str(trainer_id)
        )
        # self.trainer_certification_id = trainer_certification_id
