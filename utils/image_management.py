from fastapi import UploadFile, status, Request
from fastapi.exceptions import HTTPException
from logging_config import log
from config import IMAGES_UPLOAD_FOLDER
from utils.date_time import get_current_utc_datetime
import re
import os
import aiofiles
import aiofiles.os
import hashlib
from data.dbapis.uploaded_imges.write_queries import save_uploaded_image, delete_uploaded_image
from data.dbapis.uploaded_imges.read_queries import get_uploaded_image_by_id
from models.uploaded_image import UploadedImageInternal


async def save_image(image_file: UploadFile) -> str:
    """
    saves the provided image and returns the image_id that can be used to access the image
    :param image_file: The image file. A file-like object.
    :return: The image_id which can further be used to access tha image.
    """
    log.info(f"inside save_image(filename={image_file.filename})")

    filename = image_file.filename

    extension = filename.split(".")[-1]

    if extension not in ("jpg", "jpeg", "png", "webp", "heif", "heic"):
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="file extension must be one of jpg, jpeg, png, webp, heif, heic"
        )

    secure_filename = generate_secure_filename(filename)

    file_path = os.path.join(IMAGES_UPLOAD_FOLDER, secure_filename)

    async with aiofiles.open(file_path, "wb") as buffer:
        while chunk := await image_file.read(1024):
            await buffer.write(chunk)

    upload_image_internal = UploadedImageInternal(
        image_path=file_path
    )

    uploaded_image_id = save_uploaded_image(uploaded_image=upload_image_internal)

    log.info(f"returning {uploaded_image_id}")

    return uploaded_image_id


def generate_image_url(image_id: str, request: Request) -> str:
    """
    returns the url for the image
    :param image_id: the id of the targeted image
    :param request: the fastapi Request
    :return: the generated URL of the image
    """
    return f"{request.base_url}images/{image_id}"


def get_image_file_path(image_id: str) -> str:
    """
    returns the file_path of the image
    :param image_id: the id of the image
    :return: the file path of the image
    """
    result = get_uploaded_image_by_id(uploaded_image_id=image_id)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="image not found"
        )
    return result.image_path


async def delete_image(image_id: str) -> bool:
    uploaded_image = get_uploaded_image_by_id(uploaded_image_id=image_id)

    if uploaded_image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="image not found"
        )

    # delete the database entry
    delete_image_result = delete_uploaded_image(uploaded_image_id=image_id)

    if not delete_image_result:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="cannot delete image"
        )

    # remove the file from the file-system
    await aiofiles.os.remove(uploaded_image.image_path)

    return True


def generate_secure_filename(filename):
    """
    Sanitizes a filename to ensure it's safe and compatible with most file systems.
    """
    # generate current utc datetime hash to make the filename unique
    hash_str = hashlib.sha256(str(get_current_utc_datetime()).encode()).hexdigest()

    filename_splitted = filename.split(".")

    filename = "".join(filename_splitted[:-1]) + hash_str + "." + filename_splitted[-1]

    # Replace spaces with underscores
    filename = filename.replace(' ', '_')

    # Remove any characters that are not alphanumeric, underscores, or dots
    filename = re.sub(r'[^\w\.\-]', '', filename)

    # Limit the filename length
    max_filename_length = 255  # Example maximum length
    filename = filename[:max_filename_length]

    return filename
