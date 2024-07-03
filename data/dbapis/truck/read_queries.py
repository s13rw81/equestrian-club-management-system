from typing import List

from pymongo.cursor import Cursor

from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.truck.enums import TruckAvailability
from utils.logistics_utils import LOGISTICS_SERVICE_COLLECTION_MAPPING

truck_collection = get_collection(collection_name="trucks")


def get_trucks_by_logistics_company_id(
    logistics_company_id: str, fields: List
) -> Cursor:
    """get list of trucks that the company owns

    Args:
        logistics_company_id (str): the company id for which to fetch the trucks

    Returns:
        dict: list of trucks
    """

    log.info(f"get_trucks_by_logistics_company_id() invoked : {logistics_company_id}")

    filter = {"logistics_company_id": logistics_company_id}

    trucks_list = truck_collection.find(filter=filter, projection=fields)

    log.info(f"get_trucks_by_logistics_company_id() returning")

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


def get_trucks_by_service_id(service_id: str, service_type: str) -> List[str]:
    """get all trucks id based on logistics service id and service type

    Args:
        service_id (str): logistics service id
        service_type (str): type of logistics service

    Returns:
        List[str]: list of trucks id
    """
    log.info(f"get_trucks_by_service_id() invoked : {service_id} {service_type}")

    service_collection = LOGISTICS_SERVICE_COLLECTION_MAPPING.get(service_type, None)
    if service_collection is None:
        return None

    filter = {"_id": convert_to_object_id(service_id)}
    projection = {"trucks": True, "_id": False}
    trucks_for_service = service_collection.find(filter, projection)

    trucks = []
    for trucks_for_service in trucks_for_service:
        truck_ids = trucks_for_service["trucks"]
        for truck_id in truck_ids:
            trucks.append(str(truck_id))

    log.info(f"get_trucks_by_service_id() returning : {trucks}")

    return trucks


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


def is_truck_registered(registration_number: str) -> bool:
    """based on the registration number returns if the truck is registered with
    khayyal

    Args:
        registration_number (str)

    Returns:
        bool
    """

    filter = {"registration_number": registration_number}
    registration_count = truck_collection.count_documents(filter=filter, limit=1)

    return True if registration_count > 0 else False
