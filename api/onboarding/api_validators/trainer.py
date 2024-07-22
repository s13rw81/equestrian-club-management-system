from typing import Annotated, List

from fastapi import Depends, HTTPException, UploadFile, status

from data.dbapis.clubs.read_queries import get_club_by_id_logic
from data.dbapis.trainer.read_queries import get_trainer_details_by_email_db
from logging_config import log
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl

from ..models import AddTrainer, UpdateTrainer

user_dependency = Annotated[
    UserInternal,
    Depends(RoleBasedAccessControl(allowed_roles={UserRoles.USER})),
]

trainer_dependency = Annotated[
    UserInternal, Depends(RoleBasedAccessControl(allowed_roles={UserRoles.TRAINER}))
]


class BaseTrainerValidator:
    http_exception = lambda message: HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail=message
    )

    def __init__(self, user: user_dependency) -> None:
        self.user = user

        if not self.user.otp_verified:
            raise BaseTrainerValidator.http_exception(
                message="otp verification required"
            )


class AddTrainerValidator(BaseTrainerValidator):
    def __init__(self, user: user_dependency, trainer_details: AddTrainer) -> None:
        super().__init__(user)
        self.trainer_details = trainer_details

        if self.validate_if_email_exists(
            email_address=self.trainer_details.email_address
        ):
            raise BaseTrainerValidator.http_exception(
                message="trainer with same email already exists"
            )

        if self.validate_club_id(club_id=self.trainer_details.club_id):
            raise BaseTrainerValidator.http_exception(
                message="club_id should be a valid club id"
            )

    @staticmethod
    def validate_if_email_exists(email_address: str) -> bool:
        return (
            True
            if get_trainer_details_by_email_db(email_address=email_address)
            else False
        )

    @staticmethod
    def validate_club_id(club_id: str) -> bool:
        return True if get_club_by_id_logic(club_id=club_id) else False


class UpdateTrainerValidator(BaseTrainerValidator):
    def __init__(
        self, user: trainer_dependency, trainer_details: UpdateTrainer
    ) -> None:
        super().__init__(user)
        self.trainer_details = trainer_details

        if self.validate_if_email_exists(
            email_address=self.trainer_details.email_address
        ):
            raise BaseTrainerValidator.http_exception(
                message="trainer with same email already exists"
            )

        if self.validate_club_id(club_id=self.trainer_details.club_id):
            raise BaseTrainerValidator.http_exception(
                message="club_id should be a valid club id"
            )

    @staticmethod
    def validate_if_email_exists(email_address: str) -> bool:
        return (
            True
            if get_trainer_details_by_email_db(email_address=email_address)
            else False
        )

    @staticmethod
    def validate_club_id(club_id: str) -> bool:
        return True if get_club_by_id_logic(club_id=club_id) else False


class UploadTrainerCertificationsValidator(BaseTrainerValidator):
    def __init__(self, user: trainer_dependency, files: List[UploadFile]) -> None:
        super().__init__(user)
        self.files = files


class UploadTrainerProfileFilesValidator(BaseTrainerValidator):
    def __init__(self, user: trainer_dependency, files: List[UploadFile]) -> None:
        super().__init__(user)
        self.files = files


class UploadTrainerProfilePictureValidator(BaseTrainerValidator):
    def __init__(self, user: trainer_dependency, file: UploadFile) -> None:
        super().__init__(user)
        self.image_file = file


class GetTrainerDetailsValidator(BaseTrainerValidator):
    def __init__(self, user: trainer_dependency) -> None:
        super().__init__(user)
