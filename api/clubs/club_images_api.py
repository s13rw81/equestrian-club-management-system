from typing import List, Annotated

from api.clubs.clubs_api import clubs_api_router
from bson import ObjectId
from data.db import async_get_clubs_collection
from data.dbapis.clubs.read_queries import async_get_club_by_id
from data.dbapis.clubs.update_queries import async_update_club_by_id
from fastapi import UploadFile, File, Depends, HTTPException
from logging_config import log
from logic.auth import get_current_user
from models.user import UserInternal
from models.user.user_external import UserExternal
from pydantic import BaseModel
from utils.async_upload_image import async_upload_image
from utils.date_time import get_current_utc_datetime


class UpdateClubImagesRequest(BaseModel):
    club_id: str
    images: UploadFile = File(...)


@clubs_api_router.post("/upload_images")
async def upload_images(user: Annotated[UserInternal, Depends(get_current_user)], club_id: str,
                        files: UploadFile = File(...)) -> dict:
    """
    :param club_id:
    :param files:
    :param user: user invoking the api
    :param request: instance of UpdateClubImagesRequest dto
    :return: instance of dict, status of image upload
    """
    log.info(f"uploading images for club {club_id}, user: {user}")
    user_ext = UserExternal(**user.model_dump())
    utc_date_time = get_current_utc_datetime()

    # Upload the images and get their paths
    image_paths = []
    # for image in files:
    path = await async_upload_image(files)
    image_paths.append(path)

    # Update the club with the new image paths
    updated_club = await async_get_club_by_id(club_id)
    if updated_club.image_urls is None:
        updated_club.image_urls = image_paths
    else:
        updated_club.image_urls.extend(image_paths)
    updated_club.update_date_time = utc_date_time
    result = await async_update_club_by_id(club_id = club_id, updated_club = updated_club)

    msg = f"uploaded {len(image_paths)} images for club {club_id} by user: {user_ext}"
    return {'status_code': 200, 'details': msg, 'data': result}


@clubs_api_router.get("/get_images/{club_id}")
async def get_club_images(club_id: str) -> dict:
    """
    Retrieves image URLs for a club based on club_id.
    """
    club_collection = await async_get_clubs_collection()
    club = await club_collection.find_one({"_id": ObjectId(club_id)})
    if not club or "image_urls" not in club:
        raise HTTPException(status_code = 404, detail = f"No images found for club with id {club_id}")

    return {'status_code': 200, 'details': f"Retrieved images for club {club_id}", 'data': club["image_urls"]}
