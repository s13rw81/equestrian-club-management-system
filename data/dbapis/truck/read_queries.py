from typing import List

from pymongo.cursor import Cursor

from data.db import get_truck_collection
from logging_config import log

truck_collection = get_truck_collection()


def get_trucks_company_by_id(company_id: str, fields: List) -> Cursor:
    """_summary_

    Args:
        company_id (str): the company id for which to fetch the trucks

    Returns:
        dict: list of trucks
    """

    log.info(f"get_trucks_by_company_id() invoked : {company_id}")

    filter = {"company_id": company_id}

    trucks_list = truck_collection.find(filter=filter, projection=fields)

    log.info(f"trucks_list {dir(trucks_list)}")

    return trucks_list
