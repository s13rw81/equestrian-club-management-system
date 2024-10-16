from fastapi import APIRouter, HTTPException, status
from role_based_access_control import RoleBasedAccessControl
from fastapi import Depends
from typing import Annotated
from models.user import UserInternal
from models.user.enums import UserRoles
from models.trainers import UpdateTrainerInternal
from models.http_responses import Success
from .models import GetTrainerDTO
from data.dbapis.trainers import update_trainer as update_trainer_db, find_trainer, find_many_trainers
from .role_based_parameter_control import UpdateTrainerParameterControl
from logic.auth import get_current_user
from logging_config import log
from datetime import datetime
import pytz

trainers_api_router = APIRouter(
    prefix="/trainers",
    tags=["trainers"]
)


@trainers_api_router.put("/update-trainer")
async def update_trainer(
        update_trainer_parameter_control: Annotated[
            UpdateTrainerParameterControl,
            Depends()
        ]
):
    update_trainer_dto = update_trainer_parameter_control.update_trainer_dto
    user = update_trainer_parameter_control.user

    log.info(
        f"inside /trainers/update-trainer ("
        f"update_trainer_dto={update_trainer_dto}, "
        f"user={user})"
    )

    update_trainer_dto = UpdateTrainerInternal(
        id=update_trainer_dto.id,
        last_updated_by=user.id,
        last_update_on=datetime.now(pytz.utc),
        **update_trainer_dto.model_dump(exclude_unset=True)
    )


    updated_trainer = update_trainer_db(update_trainer_dto=update_trainer_dto)

    log.info("trainer updated successfully, returning...")

    return Success(
        message="trainer updated successfully...",
        data={
            "updated_trainer": GetTrainerDTO(**updated_trainer.model_dump())
        }
    )


@trainers_api_router.get("/get-trainer/{trainer_id}")
async def get_trainer_by_id(
        trainer_id: str,
        user: Annotated[UserInternal, Depends(get_current_user)]
):
    log.info(f"inside /trainers/get-trainer/{trainer_id} (club_id={trainer_id}, user_id={user.id})")

    trainer = find_trainer(id=trainer_id)

    if not trainer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"no trainer exists with the provided id (trainer_id={trainer_id})"
        )

    retval = Success(
        message="trainer retrieved successfully...",
        data=GetTrainerDTO(**trainer.model_dump())
    )

    log.info(f"returning {retval}")

    return retval


@trainers_api_router.get("/get-your-trainer")
async def get_your_trainer(
        user: Annotated[
            UserInternal,
            Depends(RoleBasedAccessControl(allowed_roles={UserRoles.TRAINER}))
        ]
):
    log.info(f"inside /trainers/get-your-trainer (user_id={user.id})")

    trainer = find_trainer(user_id=str(user.id))

    retval = Success(
        message="trainer retrieved successfully...",
        data=GetTrainerDTO(**trainer.model_dump())
    )

    log.info(f"returning {retval}")

    return retval

@trainers_api_router.get("/get-trainers-by-club/{club_id}")
async def get_trainers_by_club(
        club_id: str,
        user: Annotated[
            UserInternal,
            Depends(get_current_user)
        ]
):
    log.info(f"inside /trainers/get-trainers-by-club/{club_id} (club_id={club_id}, user_id={user.id})")

    trainers = find_many_trainers(club_affiliation=club_id)

    retval = Success(
        message="trainers retrieved successfully...",
        data=[
            GetTrainerDTO(**trainer.model_dump()) for trainer in trainers
        ]
    )

    log.info(f"returning {retval}")

    return retval