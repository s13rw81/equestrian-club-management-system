from api.onboarding.models.update_company_model import UpdateCompanyModel
from bson import ObjectId
from bson.errors import InvalidId
from data.db import get_logistics_company_collection
from fastapi import HTTPException
from logging_config import log
from fastapi import status
from models.company import Company
from models.user import UserInternal

logistic_company_collection = get_logistics_company_collection()


def get_admins_of_logistic_company(company_id: str) -> list:
    log.info(f"fetching list of admins of company with company id : {company_id}")
    retval = get_logistics_company_by_id_logic(company_id = company_id)
    log.info(f"result is {retval}")
    if not retval.admins:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'logistic company with given id not found.'
        )
    return retval.admins


def get_logistics_company_by_id_logic(company_id: str) -> Company | None:
    """
    :param company_id: id of the logistics company to be fetched
    :return: instance of Company, details of the logistics company
    """

    logistics_company = None

    # fetch the logistics_company
    try:
        logistics_company = logistic_company_collection.find_one({"_id": ObjectId(company_id)})
    except InvalidId as e:
        log.error(f'{e} :  club_id')
    finally:
        if logistics_company:
            return logistics_company
        else:
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = f'no company found with id {company_id}'
            )


def update_logistics_company(user: UserInternal, company_id: str, update_company: UpdateCompanyModel):
    log.info(f"updating logistics company data")
    company = get_logistics_company_by_id_logic(company_id)

    # check if user has permission
    if company and user.id not in company['admins']:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'user is does not have privilege to use this route.'
        )
    # update the model
    update_company_dict = update_company.model_dump()

    # Update the club in the database
    result = logistic_company_collection.update_one({'_id': ObjectId(company_id)}, {'$set': update_company_dict})

    return result.modified_count == 1


