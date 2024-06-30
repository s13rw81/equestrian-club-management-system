from data.db import get_logistics_company_collection
from fastapi import HTTPException
from fastapi import status
from logging_config import log
from models.company import Company

logistics_company_collection = get_logistics_company_collection()


def save_logistics_company(new_logistics_company: Company) -> str:
    """
        saves the new user in the database and returns the id
        :param new_logistics_company: Company
        :returns: id
    """
    log.info(f"save_logistics_company invoked: {new_logistics_company}")

    # Check if a logistics_company with the same name and city already exists
    existing_club = logistics_company_collection.find_one(
        {"company_name": new_logistics_company.company_name, "address.city": new_logistics_company.address.city})


    if existing_club is not None:
        emsg = f"Logistics Company with name {new_logistics_company.name} and city {new_logistics_company.address.city} already exists."
        log.info(emsg)
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail=emsg
        )

    logistics_company_id = (logistics_company_collection.insert_one(new_logistics_company.model_dump())).inserted_id
    retval = str(logistics_company_id)
    log.info(f"new logistics company created with id: {retval}")
    return retval
