from data.dbapis.trainers import save_trainer
from data.dbapis.user import update_user
from logging_config import log
from models.trainers import TrainerInternal
from models.user import UserInternal, UpdateUserInternal
from models.user.enums import UserRoles
from decorators import atomic_transaction

@atomic_transaction
def create_trainer(trainer: TrainerInternal, user: UserInternal, session=None) -> TrainerInternal:

    log.info(f"inside create_trainer(trainer={trainer}, user={user})")

    newly_created_trainer = save_trainer(new_trainer=trainer, session=session)

    update_user_dto = UpdateUserInternal(
        id=str(user.id),
        user_role=UserRoles.TRAINER
    )

    update_user(update_user_dto=update_user_dto, session=session)

    log.info(f"returning {newly_created_trainer}")

    return newly_created_trainer