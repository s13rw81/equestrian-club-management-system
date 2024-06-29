from data.db import get_uploaded_images_collection, convert_to_object_id
from models.uploaded_image import UploadedImageInternal
from logging_config import log
from typing import Optional

uploaded_images_collection = get_uploaded_images_collection()


def get_uploaded_image_by_id(uploaded_image_id: str) -> Optional[UploadedImageInternal]:
    """
    if record exists for the provided id,
    returns the record otherwise None

    :param uploaded_image_id: the _id of the database record
    :return: UploadImageInternal if record exists otherwise None
    """

    log.info(f"inside get_uploaded_image_by_id(uploaded_image_id={uploaded_image_id})")

    uploaded_image = uploaded_images_collection.find_one({"_id": convert_to_object_id(uploaded_image_id)})

    if uploaded_image is None:
        retval = None
    else:
        retval = UploadedImageInternal(**uploaded_image)

    log.info(f"returning {retval}")
    return retval
