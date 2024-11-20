from typing import Annotated

from fastapi import Depends, HTTPException, status

from data.dbapis.clubs import find_club, find_club_by_user
from logging_config import log
from models.user.enums import UserRoles
from models.user.user_internal import UserInternal
from role_based_access_control import RoleBasedAccessControl

from ..models.club_service import AddClubServiceRequest


class ClubServiceParameterControl:
    def __init__(
        self,
        user: Annotated[
            UserInternal,
            Depends(
                RoleBasedAccessControl(allowed_roles={UserRoles.CLUB, UserRoles.ADMIN})
            ),
        ],
        club_service: AddClubServiceRequest,
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

            log.info(
                f"club.club_id {club.club_id}, club_service_club_id {club_service.club_id}"
            )

            if str(club.id) != club_service.club_id:
                log.info("user is not authorized to add service to this club...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user is not authorized to add service to this club...",
                )

        if user.user_role == UserRoles.ADMIN:
            log.info("user role is admin; validating club_id...")

            club = find_club(id=club_service.club_id)

            if not club:
                log.info(f"invalid club_id={club_service.club_id}...")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"invalid club_id={club_service.club_id}",
                )

        self.user = user
        self.club_service = club_service
