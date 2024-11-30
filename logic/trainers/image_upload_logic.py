from datetime import datetime

import pytz
from fastapi import UploadFile

from data.dbapis.trainer_certifications import (
    find_trainer_certification,
    update_trainer_certifications_bulk,
)
from logging_config import log
from models.trainer_certification import (
    TrainerCertificationInternal,
    UpdateTrainerCertificationInternal,
)
from utils.image_management import delete_image, save_image


async def upload_trainer_certificate_image(
    certificate_id: str, image: UploadFile
) -> TrainerCertificationInternal:
    log.info(
        f"inside upload_trainer_certificate_image(certificate_id={certificate_id}, "
        f"image_filename={image.filename})"
    )

    trainer_certification = find_trainer_certification(id=certificate_id)

    existing_image_id = trainer_certification.image

    if existing_image_id:
        log.info("image already exists, deleting existing image...")
        await delete_image(image_id=existing_image_id)

    new_image_id = await save_image(image_file=image)

    update_trainer_certification_dto = UpdateTrainerCertificationInternal(
        id=trainer_certification.id,
        last_updated_on=datetime.now(pytz.utc),
        image=new_image_id,
    )

    updated_trainer_certifications = update_trainer_certifications_bulk(
        update_trainer_certification_dtos=[update_trainer_certification_dto]
    )

    retval = updated_trainer_certifications[0]

    log.info(f"returning {retval}")

    return retval
