from typing import Annotated

from api.onboarding.models import CreatelogisticsCompanyRequest
from api.onboarding.models.update_company_model import UpdateCompanyModel
from api.onboarding.onboarding_router import onboarding_api_router
from bson import ObjectId
from data.db import get_logistics_company_collection
from data.dbapis.logistics.logistics_company import save_logistics_company
from fastapi import Depends, HTTPException, UploadFile, Request
from fastapi import status
from logging_config import log
from logic.auth import get_current_user
from logic.onboarding.logistics import update_logistics_company, \
    get_logistics_company_by_id_logic
from models.logistic_company.logistic_company_internal import LogisticCompanyInternal
from models.user import UserInternal
from models.user.user_external import UserExternal
from utils.image_management import generate_image_url, save_image

logistics_company_collection = get_logistics_company_collection()


@onboarding_api_router.post("/create-logistic-company")
async def create_logistics_company(create_new_logistics_company: CreatelogisticsCompanyRequest,
                                   user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    """
    :param user: user invoking the api
    :param create_new_logistics_company: instace of Createlogistics_company dto
    :return: instance of str, id of new logistics_company created
    """
    # TODO: [phase ii] check if user has permission to add logistics_company
    log.info(f"creating logistics_company, user: {user}")
    if user.otp_verified is False:
        raise HTTPException(
            status_code = status.HTTP_428_PRECONDITION_REQUIRED,
            detail = 'User must be OTP verified.'
        )
    user_ext = UserExternal(**user.model_dump())
    # Convert the request model to the DB model
    new_logistics_company_internal = LogisticCompanyInternal(**create_new_logistics_company.dict(), users = [user.id])
    result = save_logistics_company(new_logistics_company_internal)
    msg = f"new logistics_company created with id: {result} by user: {user_ext}"
    return {'status_code': 201, 'details': msg, 'data': result}


@onboarding_api_router.post("/logistic-company-upload-images")
async def upload_images_for_logistic_company_by_id(company_id: str, images: list[UploadFile],
                                                   user: Annotated[UserInternal, Depends(get_current_user)]):
    user_ext = UserExternal(**user.model_dump())
    log.info(f'uploading images for logistic company. {images} by {user_ext} for company_id: {company_id}')

    # check if user is admin of logistic company

    image_ids = []
    for image in images:
        uploaded_image_id = await save_image(image_file = image)
        image_ids.append(uploaded_image_id)

    update_company = UpdateCompanyModel(images = image_ids)
    # Update the club with the new image ids
    result = update_logistics_company(company_id = company_id, user = user, update_company = update_company)
    if not result:
        emsg = f'company with id : {company_id} not found.'
        log.error(emsg)
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = emsg
        )
    msg = f"uploaded {len(image_ids)} images for logistics company {company_id} by user: {user_ext}"
    log.info(msg)
    return {'status_code': 200, 'details': msg, 'data': result}


@onboarding_api_router.get("/get_logistics_company_images/{company_id}")
async def get_company_images_by_id( request: Request, company_id: str = None) -> dict:
    """
    Retrieves image URLs for a club based on club_id.
    """

    company = logistics_company_collection.find_one({"_id": ObjectId(company_id)})
    if not company or "images" not in company:
        raise HTTPException(status_code = 404, detail = f"No images found for company with id {company_id}")

    generated_url_list = [generate_image_url(image_id = image_id, request = request) for image_id in company['images']]

    return {'status_code': 200, 'details': f"Retrieved images for company {company_id}", 'data': generated_url_list}


@onboarding_api_router.get("/get_logistics_company/{company_id}")
async def get_logistics_company_by_id(company_id: str,
                                      user: Annotated[UserInternal, Depends(get_current_user)]) -> dict:
    # if user.id not in get_admins_of_logistic_company(company_id):

    company = get_logistics_company_by_id_logic(company_id = company_id)
    if not company:
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = f'no company found with id')
    if company.admins and user.id in company.admins:
        return {'status_code': 200, 'detail': f'company found with id {company_id}', 'data': company.model_dump()}
    else:
        raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED,
                            detail = f'user does not have priviledge to access this route.')
