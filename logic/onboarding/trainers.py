from api.onboarding.models import (
    CreateTrainerCertificationDTO,
    CreateTrainerSpecializationDTO,
)
from data.dbapis.trainer_certifications import save_trainer_certifications_bulk
from data.dbapis.trainer_specializations import save_trainer_specializations_bulk
from data.dbapis.trainers import save_trainer
from data.dbapis.user import update_user
from decorators import atomic_transaction
from logging_config import log
from logic.trainers import trainers_get_query_with_pagination
from models.trainer_certification import TrainerCertificationInternal
from models.trainer_specialization import TrainerSpecializationInternal
from models.trainers import TrainerDetailedInternal, TrainerInternal
from models.user import UpdateUserInternal, UserInternal
from models.user.enums import UserRoles


@atomic_transaction
def create_trainer_logic(
    trainer: TrainerInternal,
    user: UserInternal,
    trainer_certifications: list[CreateTrainerCertificationDTO] = None,
    trainer_specializations: list[CreateTrainerSpecializationDTO] = None,
    session=None,
) -> TrainerDetailedInternal:

    log.info(
        f"inside create_trainer(trainer={trainer}, trainer_certifications={trainer_certifications}, "
        f"trainer_specializations={trainer_specializations}, user={user})"
    )

    # creating the trainer
    newly_created_trainer = save_trainer(new_trainer=trainer, session=session)

    # new_trainer_certifications = [
    #     TrainerCertificationInternal(
    #         created_by=str(user.id),
    #         trainer_id=str(newly_created_trainer.id),
    #         **trainer_certification.model_dump(),
    #     )
    #     for trainer_certification in trainer_certifications
    # ]

    # # creating the trainer_certifications
    # save_trainer_certifications_bulk(
    #     new_trainer_certifications=new_trainer_certifications, session=session
    # )

    # new_trainer_specializations = [
    #     TrainerSpecializationInternal(
    #         created_by=str(user.id),
    #         trainer_id=str(newly_created_trainer.id),
    #         **trainer_specialization.model_dump(),
    #     )
    #     for trainer_specialization in trainer_specializations
    # ]

    # # creating the trainer_specializations
    # save_trainer_specializations_bulk(
    #     new_trainer_specializations=new_trainer_specializations, session=session
    # )

    update_user_dto = UpdateUserInternal(id=str(user.id), user_role=UserRoles.TRAINER)

    # updating the user's role
    update_user(update_user_dto=update_user_dto, session=session)

    trainer_detailed = trainers_get_query_with_pagination(
        f=[f"id$eq${newly_created_trainer.id}"], session=session
    )

    retval = trainer_detailed[0]

    log.info(f"returning trainer_detailed={retval}")

    return retval
