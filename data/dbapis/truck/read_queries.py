from typing import List

from pymongo.cursor import Cursor

from data.db import convert_to_object_id, get_truck_collection
from logging_config import log
from models.truck.enums import TruckAvailability

truck_collection = get_truck_collection()


def get_trucks_company_by_id(company_id: str, fields: List) -> Cursor:
    """get list of trucks that the company owns

    Args:
        company_id (str): the company id for which to fetch the trucks

    Returns:
        dict: list of trucks
    """

    log.info(f"get_trucks_by_company_id() invoked : {company_id}")

    filter = {"company_id": company_id}

    trucks_list = truck_collection.find(filter=filter, projection=fields)

    log.info(f"get_trucks_by_company_id() returning")

    return trucks_list


def get_truck_details_by_id_db(truck_id: str, fields: List) -> dict:
    """fetches the details of the truck based on truck_id

    Args:
        truck_id (str): the id of the truck
    """

    log.info(f"get_truck_details_by_id_db() invoked : {truck_id}")

    filter = {"_id": convert_to_object_id(truck_id)}
    truck_details = truck_collection.find_one(filter=filter, projection=fields)

    log.info(f"get_truck_details_by_id_db() returning : {truck_details}")

    return truck_details


def get_available_trucks_db(
    type: str = None,
    location: str = None,
    fields: List = [],
) -> dict:
    """retrieve the list of available trucks based on the truck type or
    truck location

    Args:
        type (str)
        location (str)

    Returns:
        dict
    """

    log.info(f"inside get_available_trucks_db()")

    filter = {"availability": TruckAvailability.AVAILABLE.value}
    if type:
        filter["type"] = type

    if location:
        filter["location"] = location

    available_trucks = truck_collection.find(filter=filter, fields=fields)

    log.info(f"get_available_trucks_db() returning : {available_trucks}")

    return available_trucks
