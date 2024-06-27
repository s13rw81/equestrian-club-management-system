from data.db import get_uploaded_images_collection, convert_to_object_id
from logging_config import log
from models.uploaded_image import UploadedImageInternal

uploaded_images_collection = get_uploaded_images_collection()


def save_uploaded_image(uploaded_image: UploadedImageInternal) -> str:
    log.info(f"inside save_uploaded_image(uploaded_image={uploaded_image})")

    uploaded_image_id = (uploaded_images_collection.insert_one(uploaded_image.model_dump())).inserted_id

    retval = str(uploaded_image_id)

    log.info(f"returning {retval}")

    return retval


def delete_uploaded_image(uploaded_image_id: str) -> bool:
    log.info(f"inside delete_uploaded_image(uploaded_image_id={uploaded_image_id})")

    result = uploaded_images_collection.delete_one({"_id": convert_to_object_id(uploaded_image_id)})

    log.info(f"deleted count = {result.deleted_count}")

    return result.deleted_count == 1
