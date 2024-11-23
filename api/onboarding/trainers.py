from typing import Annotated
from .models import CreateTrainerDTO
from api.onboarding.onboarding_router import onboarding_api_router
from fastapi import Depends, HTTPException, status
from logging_config import log
from logic.onboarding.trainers import create_trainer_logic
from models.user import UserInternal
from models.user.enums import UserRoles
from models.trainers import TrainerInternal
from role_based_access_control import RoleBasedAccessControl
from models.http_responses import Success
from data.dbapis.trainer_affiliation import find_trainer_affiliation
from api.trainers.models import GetTrainerDetailedDTO


@onboarding_api_router.post("/create-trainer")
async def create_trainer(
        create_trainer_dto: CreateTrainerDTO,
        user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]
):
    log.info(f"/create-trainer invoked (create_trainer_dto={create_trainer_dto}, user_id={user.id})")

    trainer_affiliation = find_trainer_affiliation(id=create_trainer_dto.club_affiliation_number)

    if trainer_affiliation.phone_number != user.phone_number:
        log.info(f"the trainer_affiliation.phone_number: {trainer_affiliation.phone_number} does not "
                 f"match with user.phone_number: {user.phone_number}, raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="invalid trainer affiliation number"
        )

    trainer = TrainerInternal(
        created_by=user.id,
        user_id=str(user.id),
        club_id=trainer_affiliation.club_id,
        phone_number=trainer_affiliation.phone_number,
        email_address=trainer_affiliation.email_address,
        **create_trainer_dto.model_dump()
    )

    newly_created_trainer_detailed = create_trainer_logic(
        trainer=trainer,
        trainer_certifications=create_trainer_dto.certifications,
        trainer_specializations=create_trainer_dto.specializations,
        user=user
    )

    return Success(
        message="trainer created successfully",
        data=GetTrainerDetailedDTO(**newly_created_trainer_detailed.model_dump())
    )
