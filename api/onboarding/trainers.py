from typing import Annotated
from .models import CreateTrainerDTO
from api.onboarding.onboarding_router import onboarding_api_router
from fastapi import Depends
from logging_config import log
from logic.onboarding.trainers import create_trainer as create_trainer_logic
from models.user import UserInternal
from models.user.enums import UserRoles
from models.trainers import TrainerInternal
from role_based_access_control import RoleBasedAccessControl
from models.http_responses import Success


@onboarding_api_router.post("/create-trainer")
async def create_trainer(
        create_trainer_dto: CreateTrainerDTO,
        user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]
):
    log.info(f"/create-trainer invoked (create_trainer_dto={create_trainer_dto}, user_id={user.id})")

    trainer = TrainerInternal(
        created_by=user.id,
        user_id=str(user.id),
        **create_trainer_dto.model_dump()
    )

    newly_created_trainer = create_trainer_logic(trainer=trainer, user=user)

    return Success(
        message="trainer created successfully",
        data={
            "id": str(newly_created_trainer.id)
        }
    )
