from role_based_access_control import RoleBasedAccessControl
from models.user.enums import UserRoles
from models.user import UserInternal
from fastapi import Form, Depends, HTTPException, status
from data.dbapis.clubs import find_club_by_user, find_club
from typing import Annotated
from logging_config import log


class ClubIdParameterControlForm:
    def __init__(
            self,
            user: Annotated[
                UserInternal,
                Depends(RoleBasedAccessControl(allowed_roles={UserRoles.CLUB, UserRoles.ADMIN}))
            ],
            club_id: str = Form(..., description="the database uuid")
    ):
        log.info(f"inside __init__(user_id={user.id}, club_id={club_id})")

        if user.user_role == UserRoles.CLUB:
            log.info("user role is club; validating club_id...")
            club = find_club_by_user(user_id=str(user.id))

            if not club:
                log.info("user does not have an associated club... raising exception...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user does not have an associated club..."
                )

            if str(club.id) != club_id:
                log.info("user is not authorized to modify this club...")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="user is not authorized to modify this club..."
                )

        if user.user_role == UserRoles.ADMIN:
            log.info("user role is admin; validating club_id...")

            club = find_club(id=club_id)

            if not club:
                log.info(f"invalid club_id={club_id}... raising exception...")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"invalid club_id={club_id}"
                )
        self.user = user
        self.club_id = club_id