from data.dbapis.clubs import find_club, update_club
from models.clubs import UpdateClubInternal, ClubInternal
from utils.image_management import save_image, delete_image
from fastapi import UploadFile
from logging_config import log
from datetime import datetime
import pytz


async def upload_logo_logic(club_id: str, logo: UploadFile) -> ClubInternal:
    log.info(f"inside upload_logo_logic(club_id={club_id}, logo_filename={logo.filename})")

    club = find_club(id=club_id)

    existing_logo_id = club.logo

    if existing_logo_id:
        await delete_image(image_id=existing_logo_id)

    new_logo_id = await save_image(image_file=logo)

    update_club_dto = UpdateClubInternal(
        id=club_id,
        last_updated_on=datetime.now(pytz.utc),
        logo=new_logo_id
    )

    updated_club = update_club(update_club_data=update_club_dto)

    return updated_club

async def upload_images_logic(club_id: str, images: list[UploadFile]) -> ClubInternal:
    log.info(f"inside upload_images_logic(club_id={club_id}, "
             f"images_filenames={[image.filename for image in images]})")


    club = find_club(id=club_id)

    existing_image_ids = club.images

    if existing_image_ids:
        for image_id in existing_image_ids:
            await delete_image(image_id)

    new_image_ids = [await save_image(image_file=image) for image in images]

    update_club_dto = UpdateClubInternal(
        id=club_id,
        last_updated_on=datetime.now(pytz.utc),
        images=new_image_ids
    )

    updated_club = update_club(update_club_data=update_club_dto)

    return updated_club


