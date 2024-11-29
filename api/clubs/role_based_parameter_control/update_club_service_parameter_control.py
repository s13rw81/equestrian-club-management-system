from typing import Annotated

from fastapi import Depends, HTTPException, status

from data.dbapis.clubs import (
    find_club,
    find_club_by_user,
    find_club_service,
    get_club_service_availability,
)
from logging_config import log
from models.user.enums import UserRoles
from models.user.user_internal import UserInternal
from role_based_access_control import RoleBasedAccessControl

from ..models.club_service import UpdateClubServiceRequest


class UpdateClubServiceParameterControl:
    def __init__(
        self,
        club_id: str,
        club_service_id: str,
        user: Annotated[
            UserInternal,
            Depends(
                RoleBasedAccessControl(allowed_roles={UserRoles.CLUB, UserRoles.ADMIN})
            ),
        ],
        club_service: UpdateClubServiceRequest,
    ) -> None:
        log.info(f"inside __init__(user_id={user.id}, club_service={club_service})")

        if user.user_role == UserRoles.CLUB:
            log.info("user role is club; validating club_id...")
            club = find_club_by_user(user_id=str(user.id))

            if not club:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user does not have an associated club...",
                )

            log.info(f"club.club_id {club.club_id}, club_service_club_id {club_id}")

            if str(club.id) != club_id:
                log.info("user is not authorized to add service to this club...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user is not authorized to add service to this club...",
                )

            existing_club_service = find_club_service(id=club_service_id)
            if not existing_club_service:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="club service with provided id does not exists...",
                )

        if user.user_role == UserRoles.ADMIN:
            log.info("user role is admin; validating club_id...")

            club = find_club(id=club_id)

            if not club:
                log.info(f"invalid club_id={club_id}...")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"invalid club_id={club_id}",
                )

        self.user = user
        self.club_id = club_id
        self.club_service = club_service
        self.club_service_id = club_service_id
        log.info(f"type_of_club_service {type(self.club_service)}")

        availability_validated = self.validate_availability()
        if not availability_validated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="cannot validate the provided availability",
            )

    def validate_availability(self):
        if not self.club_service.availability:
            return True

        for availability in self.club_service.availability:
            is_valid_availability = get_club_service_availability(
                club_service_id=self.club_service_id,
                availability_id=availability.availability_id,
            )
            if not is_valid_availability:
                log.error("cannot validate the provided availability")
                return False

        return True