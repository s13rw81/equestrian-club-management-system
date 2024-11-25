from api.clubs.models.club_service import Availability, UpdateAvailability
from data.dbapis.clubs import save_club_service, save_club_service_availability
from data.dbapis.clubs import update_club_service as update_club_service_db
from data.dbapis.clubs import update_club_service_availability
from decorators import atomic_transaction
from logging_config import log
from models.clubs.service_internal import (
    AvailabilityInternal,
    ClubServiceInternal,
    UpdateClubServiceInternal,
)
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
            **availability.model_dump(),
            club_service_id=club_service_id,
            created_by=str(user.id),
        )
        for availability in service_availability
    ]

    save_club_service_availability(
        service_availability=availability_internal, session=session
    )

    log.info(f"returning {newly_created_club_service}")

    return newly_created_club_service


@atomic_transaction
def update_club_service(
    club_service: UpdateClubServiceInternal,
    user: UserInternal,
    club_service_id: str,
    service_availability: UpdateAvailability,
    session=None,
) -> ClubServiceInternal:

    log.info(
        f"inside update_club_service; club_service={club_service}, user_id={user.id}"
    )

    updated_club_service = update_club_service_db(update_club_service_data=club_service)

    if service_availability:
        update_availability = [
            AvailabilityInternal(
                **availability.model_dump(exclude={"availability_id"}),
                id=availability.availability_id,
                club_service_id=club_service_id,
                last_updated_by=str(user.id),
            )
            for availability in service_availability
        ]
        update_club_service_availability(
            update_availability=update_availability,
            club_service_id=club_service_id,
            session=session,
        )

    return updated_club_service
