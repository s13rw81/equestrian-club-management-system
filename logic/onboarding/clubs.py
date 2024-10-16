from data.dbapis.clubs import save_club
from data.dbapis.user import update_user
from logging_config import log
from models.clubs import ClubInternal
from models.user import UserInternal, UpdateUserInternal
from models.user.enums import UserRoles
from decorators import atomic_transaction


@atomic_transaction
def create_club(club: ClubInternal, user: UserInternal, session=None) -> ClubInternal:

    log.info(f"inside create_club(club={club}, user={user})")

    newly_created_club = save_club(new_club=club, session=session)

    update_user_dto = UpdateUserInternal(
        id=user.id,
        user_role=UserRoles.CLUB
    )

    update_user(update_user_dto=update_user_dto, session=session)

    log.info(f"returning {newly_created_club}")

    return newly_created_club

