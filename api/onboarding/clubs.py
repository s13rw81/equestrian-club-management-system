from typing import Annotated
from api.onboarding.models import CreateClubRequest
from api.onboarding.models.get_club_response_model import GetClubResponse
from api.onboarding.models.update_club_model import UpdateClubRequest
from api.onboarding.onboarding_router import onboarding_api_router
from data.dbapis.club_services_generic_activity.read_queries import get_existing_generic_activity_service_for_club
from data.dbapis.club_services_horse_shoeing.read_queries import get_existing_horse_shoeing_service_for_club
from data.dbapis.club_services_riding_lessons.read_queries import get_existing_riding_lesson_service_for_club
from data.dbapis.user import update_user
from data.dbapis.clubs import save_club
from fastapi import Depends, UploadFile, HTTPException
from fastapi import status
from fastapi.requests import Request
from logging_config import log
from logic.auth import get_current_user
from logic.club_services_generic_activity.generic_activity_service import \
    update_generic_activity_service_by_club_id_logic
from logic.horse_shoeing_service.horse_shoeing_service import update_horse_shoeing_service_by_club_id_logic
from logic.onboarding.clubs import update_club_by_id_logic, get_club_id_of_user, \
    update_riding_lesson_service_by_club_id_logic
from models.user import UserInternal, UserRoles, UpdateUserInternal
from models.user.user_external import UserExternal
from models.clubs import ClubInternal, ClubUser
from role_based_access_control import RoleBasedAccessControl
from utils.image_management import save_image, generate_image_url
from models.http_responses import Success, Failed


@onboarding_api_router.post("/create-club")
async def create_club(
        create_club_request: CreateClubRequest,
        user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]
):
    """
    :param user: user invoking the api
    :param create_club_request: instance of CreateClub dto
    :return: instance of str, id of new club created
    """
    log.info(f"/create-club invoked (create_club_request={create_club_request}, user_id={user.id})")

    club = ClubInternal(
        users=[
            ClubUser(user_id=user.id)
        ],
        **create_club_request.model_dump()
    )

    newly_created_club = save_club(new_club=club)

    update_user_data = UpdateUserInternal(
        user_role=UserRoles.CLUB
    )

    user_update_result = update_user(update_user_data=update_user_data, user=user)

    return Success(
        status=200,
        message="club created successfully",
        data={
            "id": newly_created_club.id
        }
    )


@onboarding_api_router.post("/club/upload-images")
async def upload_images_for_club_by_id(images: list[UploadFile], request: Request,
                                       user: Annotated[UserInternal, Depends(get_current_user)]):
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
    club_id = str(club['_id'])
    # get riding_lesson_service for club
    riding_lesson_service = get_existing_riding_lesson_service_for_club(club_id=club_id)
    horse_shoeing_service = get_existing_horse_shoeing_service_for_club(club_id=club_id)
    generic_activity_service = get_existing_generic_activity_service_for_club(club_id=club_id)

    club_resp = GetClubResponse(**club, id=club_id, riding_lesson_service=riding_lesson_service,
                                horse_shoeing_service=horse_shoeing_service,
                                generic_activity_service=generic_activity_service)
    return club_resp.model_dump()


@onboarding_api_router.put("/update-club")
async def update_club(user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.CLUB}))], update_club_request: UpdateClubRequest):
    log.info(f'updating club associated with user {user}')

    # get the club associated with user in request
    club = get_club_id_of_user(user=user)
    if not club:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no club assiocated with user')

    club_id = str(club['_id'])
    log.info(f'club assotiated with user {user} is {club}')

    # update club document
    res_update_club = update_club_by_id_logic(club_id=club_id, updated_club = update_club_request)
    res_update_riding_lesson_service = update_riding_lesson_service_by_club_id_logic(club_id=club_id, updated_club = update_club_request)
    res_update_horse_shoeing_service = update_horse_shoeing_service_by_club_id_logic(club_id=club_id, updated_club = update_club_request)
    res_update_generic_activity_service = update_generic_activity_service_by_club_id_logic(club_id=club_id, updated_club = update_club_request)
    if log.info(f'result of updates : res_update_club : {res_update_club}, res_update_riding_lesson_service: {res_update_riding_lesson_service}, res_update_horse_shoeing_service: {res_update_horse_shoeing_service}, res_update_generic_activity_service: {res_update_generic_activity_service}'):
        return {"status": "OK"}
    else:
        raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = 'error updating club or its services')


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
