from typing import Annotated

from api.onboarding.models import CreatelogisticsCompanyRequest
from data.dbapis.logistics.logistics_company import save_logistics_company
from fastapi import Depends, HTTPException
from logging_config import log
from logic.auth import get_current_user
from models.company import Company
from models.user import UserInternal
from models.user.user_external import UserExternal
from api.onboarding.onboarding_router import onboarding_api_router
from starlette import status


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
    new_logistics_company_internal = Company(**create_new_logistics_company.dict(), admins=[user_ext])
    result = save_logistics_company(new_logistics_company_internal)
    msg = f"new logistics_company created with id: {result} by user: {user_ext}"
    return {'status_code': 201, 'details': msg, 'data': result}
