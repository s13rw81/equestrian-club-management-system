from fastapi import UploadFile
from data.dbapis.user import update_user, find_user
from utils.image_management import save_image, delete_image
from models.user import UpdateUserInternal, UserInternal
from logging_config import log
from datetime import datetime
import pytz


async def upload_image_user_logic(user_id: str, image: UploadFile) -> UserInternal:
    log.info(f"inside upload_image_user_logic(user_id={user_id}, image_filename={image.filename}")

    user = find_user(id=user_id)

    existing_image_id = user.image

    if existing_image_id:
        log.info("image already exists, deleting existing image...")
        await delete_image(image_id=existing_image_id)

    new_image_id = await save_image(image_file=image)

    update_user_dto = UpdateUserInternal(
        id=user_id,
        last_updated_on=datetime.now(pytz.utc),
        image=new_image_id
    )

    updated_user = update_user(update_user_dto=update_user_dto)

    return updated_user

