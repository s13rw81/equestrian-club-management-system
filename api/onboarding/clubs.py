from typing import Annotated

from api.onboarding.models.update_club_model import UpdateClubRequest
from api.onboarding.models import CreateClubRequest
from api.user.models import UpdateUserRole
from bson import ObjectId
from data.db import get_clubs_collection
from data.dbapis.clubs import save_club, get_club_by_id_logic
from fastapi import Depends, UploadFile, HTTPException
from logging_config import log
from logic.auth import get_current_user
from logic.onboarding.clubs import update_club_by_id_logic
from logic.onboarding.upgrade_user import upgrade_user_role
from models.clubs import ClubInternal
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from api.onboarding.onboarding_router import onboarding_api_router
from fastapi import status
from fastapi.requests import Request
from role_based_access_control import RoleBasedAccessControl
from utils.image_management import save_image, generate_image_url

club_collection = get_clubs_collection()


@onboarding_api_router.post("/create-club")
async def create_club(create_new_club: CreateClubRequest,
                      user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    """
    :param user: user invoking the api
    :param create_new_club: instace of CreateClub dto
    :return: instance of str, id of new club created
    """
    # TODO: [phase ii] check if user has permission to add club
    log.info(f"creating club, user: {user}")
    user_ext = UserExternal(**user.model_dump())
    # Convert the request model to the DB model
    new_club_internal = ClubInternal(**create_new_club.dict(), users = [user.id])
    result = save_club(new_club_internal)
    user_role = UpdateUserRole(user_role = UserRoles.CLUB)
    res = upgrade_user_role(user_role, user)
    log.info(f'user upgraded {res}')
    msg = f"new club created with id: {result} by user: {user_ext}"
    return {'status_code': 201, 'details': msg, 'data': result}


@onboarding_api_router.post("/club/upload-images")
async def upload_images_for_club_by_id(club_id: str, images: list[UploadFile],
                                       user: Annotated[UserInternal, Depends(get_current_user)]):
    user_ext = UserExternal(**user.model_dump())
    log.info(f'uploading images for club. {images} by {user_ext} for club_id: {club_id}')

    image_ids = []
    for image in images:
        uploaded_image_id = await save_image(image_file = image)
        image_ids.append(uploaded_image_id)

    # existing_club = get_club_by_id_logic(club_id = club_id)
    update_club = UpdateClubRequest(images = image_ids)

    # Update the club with the new image ids
    result = update_club_by_id_logic(club_id = club_id, updated_club = update_club, user = user)
    if not result:
        emsg = f'company with id : {club_id} not found.'
        log.error(emsg)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = emsg
        )
    msg = f"uploaded {len(image_ids)} images for logistics company {club_id} by user: {user_ext}"
    log.info(msg)
    return {'status_code': 200, 'details': msg, 'data': result}


@onboarding_api_router.get("/onboarding/get-club-images/{club_id}")
async def get_club_images_by_id(request: Request, club_id: str = None) -> dict:
    """
    Retrieves image URLs for a club based on club_id.
    """

    club = club_collection.find_one({"_id": ObjectId(club_id)})
    if not club or club['images'] is None:
        raise HTTPException(status_code = 404, detail = f"No images found for club with id {club_id}")

    generated_url_list = [generate_image_url(image_id = image_id, request = request) for image_id in club['images']]

    return {'status_code': 200, 'details': f"Retrieved images for club {club_id}", 'data': generated_url_list}


@onboarding_api_router.get("/get-club/{club_id}")
async def get_club_by_id(club_id: str, user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.CLUB}))]) -> dict:
    club = get_club_by_id_logic(club_id = club_id).model_dump()
    if not club:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'no club found with id')
    if user.id in club['users']:
        club['_id'] = str(club['_id'])
        return {'status_code': 200, 'detail': f'club found with id {club_id}', 'data': club}
    else:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = f'user does not have priviledge to access this route.')
