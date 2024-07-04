from data.db import get_logistics_company_collection
from logging_config import log
from models.logistic_company.logistic_company_internal import LogisticCompanyInternal

logistics_company_collection = get_logistics_company_collection()


def save_logistics_company(new_logistics_company: LogisticCompanyInternal) -> str:
    """
        saves the new user in the database and returns the id
        :param new_logistics_company: Company
        :returns: id
    """
    log.info(f"save_logistics_company invoked: {new_logistics_company}")

    logistics_company_id = (logistics_company_collection.insert_one(new_logistics_company.model_dump())).inserted_id
    retval = str(logistics_company_id)
    log.info(f"new logistics company created with id: {retval}")
    return retval
