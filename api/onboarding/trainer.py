from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from data.dbapis.trainer.read_queries import get_trainer_details_by_email_db
from data.dbapis.trainer.write_queries import add_trainer, update_trainer_details
from data.dbapis.user.write_queries import update_user_role
from logging_config import log
from models.trainer.trainer import TrainerInternal
from models.user.enums.user_roles import UserRoles
from utils.date_time import get_current_utc_datetime
from utils.image_management import generate_image_url, generate_image_urls, save_image

from .api_validators.trainer import (
    AddTrainerValidator,
    GetTrainerDetailsValidator,
    UpdateTrainerValidator,
    UploadTrainerCertificationsValidator,
    UploadTrainerProfileFilesValidator,
    UploadTrainerProfilePictureValidator,
)
from .models import ResponseAddTrainer, ResponseGetTrainer, ViewTrainer
from .onboarding_router import onboarding_api_router


@onboarding_api_router.post(path="/create-trainer")
def create_trainer(
    request: Request, payload: Annotated[AddTrainerValidator, Depends()]
) -> ResponseAddTrainer:
    log.info(f"{request.url.path} invoked")

    user = payload.user
    trainer_details = payload.trainer_details

    trainer = TrainerInternal(**trainer_details.model_dump(), user_id=user.id)

    trainer_id = add_trainer(trainer=trainer)
    user_role_updated = update_user_role(user_role=UserRoles.TRAINER, user=user)

    if not user_role_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error while adding trainer",
        )

    response = ResponseAddTrainer(trainer_id=trainer_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@onboarding_api_router.put(path="/update-trainer")
def update_trainer(
    request: Request, payload: Annotated[UpdateTrainerValidator, Depends()]
):
    log.info(f"{request.url.path} invoked")

    user = payload.user
    update_details = payload.trainer_details.model_dump(exclude_none=True)

    details_updated = update_trainer_details(
        update_details=update_details, user_id=user.id
    )

    if not details_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error while updating trainer details",
        )

    return {"status": "OK"}


@onboarding_api_router.post(path="/trainer/upload-certifications")
async def upload_trainer_certifications(
    request: Request,
    payload: Annotated[UploadTrainerCertificationsValidator, Depends()],
):

    user = payload.user
    files = payload.files

    log.info(f"{request.url.path} invoked")

    image_ids = []
    for file in files:
        image_id = await save_image(image_file=file)
        image_ids.append(image_id)

    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_details = {
        "updated_at": get_current_utc_datetime(),
        "certifications": image_ids,
    }
    details_updated = update_trainer_details(
        update_details=update_details, user_id=user.id
    )
    if not details_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error while saving certifications",
        )

    return {"status": "OK"}


@onboarding_api_router.post(path="/trainer/upload-profile-files")
async def upload_trainer_profile_files(
    request: Request,
    payload: Annotated[UploadTrainerProfileFilesValidator, Depends()],
):

    user = payload.user
    files = payload.files

    log.info(f"{request.url.path} invoked")

    image_ids = []
    for file in files:
        image_id = await save_image(image_file=file)
        image_ids.append(image_id)

    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_details = {
        "updated_at": get_current_utc_datetime(),
        "profile_files": image_ids,
    }
    details_updated = update_trainer_details(
        update_details=update_details, user_id=user.id
    )
    if not details_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error while saving profile files",
        )

    return {"status": "OK"}


@onboarding_api_router.post(path="/trainer/upload-profile-picture")
async def upload_trainer_profile_picture(
    request: Request,
    payload: Annotated[UploadTrainerProfilePictureValidator, Depends()],
):

    user = payload.user
    file = payload.image_file

    log.info(f"{request.url.path} invoked")

    image_id = await save_image(image_file=file)

    if not image_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_details = {
        "updated_at": get_current_utc_datetime(),
        "profile_picture": image_id,
    }
    details_updated = update_trainer_details(
        update_details=update_details, user_id=user.id
    )
    if not details_updated:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error while saving profile picture",
        )

    return {"status": "OK"}


@onboarding_api_router.get(path="/get-trainer", response_model=ResponseGetTrainer)
def get_trainer(
    request: Request, payload: Annotated[GetTrainerDetailsValidator, Depends()]
):
    user = payload.user

    trainer_details = get_trainer_details_by_email_db(email_address=user.email_address)
    if not trainer_details:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="unable to fetch trainer details for current user",
        )

    trainer_details.certifications = generate_image_urls(
        image_ids=trainer_details.certifications, request=request
    )

    trainer_details.profile_files = generate_image_urls(
        image_ids=trainer_details.profile_files, request=request
    )

    trainer_details.profile_picture = generate_image_url(
        image_id=trainer_details.profile_picture, request=request
    )

    trainer_details = ViewTrainer(**trainer_details.model_dump())

    return trainer_details
