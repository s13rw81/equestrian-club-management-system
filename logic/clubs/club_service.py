from api.clubs.models.club_service import Availability
from data.dbapis.clubs import save_club_service, save_club_service_availability
from decorators import atomic_transaction
from logging_config import log
from models.clubs.service_internal import AvailabilityInternal, ClubServiceInternal
from models.user.user_internal import UserInternal


@atomic_transaction
def add_club_service(
    club_service: ClubServiceInternal,
    user: UserInternal,
    service_availability: Availability,
    session=None,
):

    log.info(f"inside add_club_service; club_service={club_service}, user_id={user.id}")

    newly_created_club_service = save_club_service(
        club_service=club_service, session=session
    )
    club_service_id = str(newly_created_club_service.id)

    availability_internal = [
        AvailabilityInternal(
            **availability.model_dump(), club_service_id=club_service_id
        )
        for availability in service_availability
    ]

    save_club_service_availability(
        service_availability=availability_internal, session=session
    )

    log.info(f"returning {newly_created_club_service}")

    return newly_created_club_service
