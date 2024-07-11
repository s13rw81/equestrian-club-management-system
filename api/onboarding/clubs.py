from typing import Annotated

from api.onboarding.models import CreateClubRequest
from api.onboarding.models.get_club_response_model import GetClubResponse
from api.onboarding.models.update_club_model import UpdateClubRequest
from api.onboarding.onboarding_router import onboarding_api_router
from api.user.models import UpdateUserRole
from data.db import get_clubs_collection
from data.dbapis.clubs import save_club
from fastapi import Depends, UploadFile, HTTPException
from fastapi import status
from fastapi.requests import Request
from logging_config import log
from logic.auth import get_current_user
from logic.onboarding.clubs import update_club_by_id_logic, get_club_id_of_user
from logic.onboarding.upgrade_user import upgrade_user_role
from models.clubs import ClubInternal
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from role_based_access_control import RoleBasedAccessControl
from utils.image_management import save_image, generate_image_url

club_collection = get_clubs_collection()


@onboarding_api_router.post("/create-club")
async def create_club(create_new_club: CreateClubRequest, user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    """
    :param user: user invoking the api
    :param create_new_club: instace of CreateClub dto
    :return: instance of str, id of new club created
    """
    # TODO: [phase ii] check if user has permission to add club
    log.info(f"creating club, user: {user}")
    user_ext = UserExternal(**user.model_dump())
    # Convert the request model to the DB model
    new_club_internal = ClubInternal(**create_new_club.dict(), users=[{"user_id": user.id}])
    result = save_club(new_club_internal)
    user_role = UpdateUserRole(user_role=UserRoles.CLUB)
    res = upgrade_user_role(user_role, user)
    log.info(f'user upgraded {res}')
    msg = f"new club created with id: {result} by user: {user_ext}"
    log.info(msg)
    # return {'status_code': 201, 'details': msg, 'data': result}
    return {"club_id": result}


@onboarding_api_router.post("/club/upload-images")
async def upload_images_for_club_by_id(images: list[UploadFile], request: Request, user: Annotated[UserInternal, Depends(get_current_user)]):
    club = get_club_id_of_user(user=user)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no club assiocated with user')

    user_ext = UserExternal(**user.model_dump())
    club_id = str(club['_id'])
    log.info(f'uploading images for club. {images} by {user_ext} for club_id: {club_id}')

    image_ids = []
    for image in images:
        uploaded_image_id = await save_image(image_file=image)
        image_ids.append(uploaded_image_id)

    generated_url_list = [generate_image_url(image_id=image_id, request=request) for image_id in image_ids]
    # existing_club = get_club_by_id_logic(club_id = club_id)
    update_club = UpdateClubRequest(image_urls=generated_url_list)

    # Update the club with the new image ids
    result = update_club_by_id_logic(club_id=club_id, updated_club=update_club)
    if not result:
        emsg = f'company with id : {club_id} not found.'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )
    msg = f"uploaded {len(image_ids)} images for logistics company {club_id} by user: {user_ext}"
    log.info(msg)
    return {'status': 'OK'}
    # return {'status_code': 200, 'details': msg, 'data': result}


@onboarding_api_router.get("/get-club")
async def get_club(user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.CLUB}))]) -> dict:
    club = get_club_id_of_user(user=user)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no club assiocated with user')

    # return {'status_code': 200, 'detail': f'club found with id {club_id}', 'data': club}
    del (club['id'])
    club_resp = GetClubResponse(**club, id=str(club['_id']))

    return club_resp.model_dump()

# @onboarding_api_router.get("/onboarding/get-club-images/")
# async def get_club_images_by_id(request: Request, user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.CLUB}))]) -> dict:
#     """
#     Retrieves image URLs for a club based on club_id.
#     """
#     club_id = get_club_id_of_user(user=user)
#     club = club_collection.find_one({"_id": ObjectId(club_id)})
#     if not club or club['images'] is None:
#         raise HTTPException(status_code=404, detail=f"No images found for club with id {club_id}")
#
#     generated_url_list = [generate_image_url(image_id=image_id, request=request) for image_id in club['images']]
#
#     return {'status_code': 200, 'details': f"Retrieved images for club {club_id}", 'data': generated_url_list}
#
