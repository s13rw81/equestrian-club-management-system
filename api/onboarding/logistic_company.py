from typing import Annotated

from api.onboarding.models import CreatelogisticsCompanyRequest
from api.onboarding.models.update_company_model import UpdateCompanyModel
from api.onboarding.onboarding_router import onboarding_api_router
from api.user.models import UpdateUserRole
from data.db import get_logistics_company_collection
from data.dbapis.logistics.logistics_company import save_logistics_company
from fastapi import Depends, HTTPException, UploadFile, Request
from fastapi import status
from logging_config import log
from logic.auth import get_current_user
from logic.onboarding.logistics import update_logistics_company, \
    get_company_id_of_user
from logic.onboarding.upgrade_user import upgrade_user_role
from models.logistic_company.logistic_company_internal import LogisticCompanyInternal
from models.user import UserInternal, UserRoles
from models.user.user_external import UserExternal
from role_based_access_control import RoleBasedAccessControl
from utils.image_management import generate_image_url, save_image

logistics_company_collection = get_logistics_company_collection()


@onboarding_api_router.post("/create-logistic-company")
async def create_logistics_company(create_new_logistics_company: CreatelogisticsCompanyRequest, user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.USER}))]) -> dict:
    """
    :param user: user invoking the api
    :param create_new_logistics_company: instace of Createlogistics_company dto
    :return: instance of str, id of new logistics_company created
    """
    # TODO: [phase ii] check if user has permission to add logistics_company
    log.info(f"creating logistics_company, user: {user}")
    if user.otp_verified is False:
        raise HTTPException(
            status_code=status.HTTP_428_PRECONDITION_REQUIRED,
            detail='User must be OTP verified.'
        )
    user_ext = UserExternal(**user.model_dump())
    # Convert the request model to the DB model
    new_logistics_company_internal = LogisticCompanyInternal(**create_new_logistics_company.dict(), users=[{"user_id": user.id}])
    result = save_logistics_company(new_logistics_company_internal)
    msg = f"new logistics_company created with id: {result} by user: {user_ext}"
    update_user = UpdateUserRole(user_role=UserRoles.LOGISTIC_COMPANY.value)
    log.info(msg)
    res = upgrade_user_role(update_user, user)
    log.info(res)
    return {"logistic_company_id": result}
    # return {'status_code': 201, 'detail': msg, 'data': result}


@onboarding_api_router.post("/logistic-company/upload-images")
async def upload_images_for_logistic_company(images: list[UploadFile], user: Annotated[UserInternal, Depends(get_current_user)], request: Request):
    company = get_company_id_of_user(user_id=user.id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no company assiocated with user')
    company_id = str(company['_id'])
    user_ext = UserExternal(**user.model_dump())
    log.info(f'uploading images for logistic company. {images} by {user_ext} for company_id: {company_id}')

    image_ids = []
    for image in images:
        uploaded_image_id = await save_image(image_file=image)
        image_ids.append(uploaded_image_id)

    # TODO: generate image urls
    generated_url_list = [generate_image_url(image_id=image_id, request=request) for image_id in image_ids]

    update_company = UpdateCompanyModel(image_urls=generated_url_list)
    # Update the club with the new image ids
    result = update_logistics_company(company_id=company_id, update_company=update_company)
    if not result:
        emsg = f'company with id : {company_id} not found.'
        log.error(emsg)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=emsg
        )
    msg = f"uploaded {len(image_ids)} images for logistics company {company_id} by user: {user_ext}"
    log.info(msg)
    # return {'status_code': 200, 'details': msg, 'data': result}
    return {'status': 'OK'}


@onboarding_api_router.get("/get-logistic-company")
async def get_logistics_company(user: Annotated[UserInternal, Depends(RoleBasedAccessControl({UserRoles.LOGISTIC_COMPANY}))]) -> dict:
    company = get_company_id_of_user(user_id=user.id)
    if not company:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no company assiocated with user')

    del(company['_id'])
    return company


# @onboarding_api_router.get("/get_logistics-company-images")
# async def get_company_images_by_id(user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
#     """
#     Retrieves image URLs for a club based on club_id.
#     """
#     company = get_company_id_of_user(user_id=user.id)
#     if not company:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='no company assiocated with user')
#     company_id = str(company['_id'])
#     if not company or "image_urls" not in company:
#         raise HTTPException(status_code=404, detail=f"No images found for company with id {company_id}")
#
#     return company['image_urls']
#     # return {'status_code': 200, 'details': f"Retrieved images for company {company_id}", 'data': generated_url_list}

