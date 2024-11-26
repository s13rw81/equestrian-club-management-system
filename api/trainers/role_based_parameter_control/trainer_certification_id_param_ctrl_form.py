from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles
from models.user import UserInternal
from fastapi import Form, Depends, HTTPException, status
from data.dbapis.trainers import find_trainer
from data.dbapis.trainer_certifications import find_trainer_certification
from typing import Annotated
from logging_config import log


class TrainerCertIdParamCtrlForm:
    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(RoleBasedAccessControl(allowed_roles={UserRoles.TRAINER, UserRoles.ADMIN}))
            ],
            trainer_certification_id: str = Form(..., description="the database uuid")
    ):
        log.info(f"inside __init__(user_id={user.id}, trainer_certification_id={trainer_certification_id})")

        trainer_certification = find_trainer_certification(id=trainer_certification_id)

        if not trainer_certification:
            log.info("invalid trainer_certification_id, raising HTTPException...")
            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="invalid trainer_certification_id..."
            )

        if user.user_role == UserRoles.TRAINER:
            log.info("user role is trainer; validating with trainer_id...")
            trainer = find_trainer(user_id=str(user.id))

            if trainer_certification.trainer_id != str(trainer.id):
                log.info("user is not authorized to modify this trainer certification...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user is not authorized to modify this trainer certification..."
                )

        self.user = user
        self.trainer_certification_id = trainer_certification_id