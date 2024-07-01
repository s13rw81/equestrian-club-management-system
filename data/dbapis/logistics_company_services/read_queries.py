from pymongo.collection import Collection

from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.company import Company
from models.logistics_company_services.logistics_company_services import (
    ClubToClubServiceInternalWithID,
    LuggageTransferServiceInternal,
    UserTransferServiceInternal,
)
from utils.logistics_utils import LOGISTICS_SERVICE_COLLECTION_MAPPING, LogisticsService

logistics_company_collection = get_collection(collection_name="logistics_company")

club_to_club_service_collection = LOGISTICS_SERVICE_COLLECTION_MAPPING.get(
    LogisticsService.CLUB_TO_CLUB.value
)
user_transfer_service_collection = LOGISTICS_SERVICE_COLLECTION_MAPPING.get(
    LogisticsService.USER_TRANSFER.value
)
luggage_transfer_service_collection = LOGISTICS_SERVICE_COLLECTION_MAPPING.get(
    LogisticsService.LUGGAGE_TRANSFER.value
)


def get_logistics_company_by_id(logistics_company_id: str) -> Company:
    """returns the logistics company details for the provided
    logistics_company_id

    Args:
        logistics_company_id (str)
    """
    log.info(
        f"get_logistics_company_by_id() invoked : logistics_company_id {logistics_company_id}"
    )
    try:
        company_details = logistics_company_collection.find_one(
            {"_id": convert_to_object_id(logistics_company_id)},
            projection={"company_name": 1, "admin_id": 1, "email": 1},
        )
    except Exception as e:
        log.error(f"Exception : get_logistics_company_by_id {str(e)}")
        company_details = None

    log.info(f" company_details {company_details}")

    if company_details:
        company_details["phone_no"] = ""
        company_details = Company(**company_details)

    log.info(f"get_logistics_company_by_id() returning : {company_details}")

    return company_details


def club_to_club_service_by_logistics_company_id(
    logistics_company_id: str,
) -> ClubToClubServiceInternalWithID:
    """return club to club service details for the provided logistics_company_id

    Args:
        logistics_company_id (str)

    Returns:
        ClubToClubServiceInternalWithID
    """

    log.info(
        f"club_to_club_service_by_logistics_company_id() invoked : logistics_company_id {logistics_company_id}"
    )

    try:
        service_details = club_to_club_service_collection.find_one(
            {"provider.provider_id": logistics_company_id}
        )
    except Exception as e:
        log.error(
            f"Exception : club_to_club_service_by_logistics_company_id() {str(e)}"
        )
        service_details = None

    log.info(f"service_details {service_details}")

    if service_details:
        service_details = ClubToClubServiceInternalWithID(**service_details)

    log.info(
        f"club_to_club_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details


def get_club_to_club_service_by_service_id(
    service_id: str,
) -> ClubToClubServiceInternalWithID:
    """return club to club service details by service id

    Args:
        service_id (str)

    Returns:
        ClubToClubServiceInternalWithID
    """
    log.info(
        f"get_club_to_club_service_by_service_id() invoked : service_id {service_id}"
    )

    try:
        service_details = club_to_club_service_collection.find_one(
            {"_id": convert_to_object_id(service_id)}
        )
    except Exception as e:
        log.error(f"Exception : get_club_to_club_service_by_service_id() {str(e)}")
        service_details = None

    if service_details:
        service_details = ClubToClubServiceInternalWithID(**service_details)

    log.info(
        f"club_to_club_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details


def get_user_transfer_service_by_logistics_company_id(
    logistics_company_id: str,
) -> UserTransferServiceInternal:
    """return the user horse transfer service details by logistics company id

    Args:
        logistics_company_id (str)

    Returns:
        UserTransferServiceInternal
    """

    service_details = user_transfer_service_collection.find_one(
        {"provider.provider_id": logistics_company_id}
    )

    if service_details:
        service_details = UserTransferServiceInternal(**service_details)

    log.info(
        f"get_user_transfer_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details


def get_user_transfer_service_by_service_id(
    service_id: str,
) -> UserTransferServiceInternal:
    """return user transfer service details by service id

    Args:
        service_id (str)

    Returns:
        UserTransferServiceInternal
    """
    log.info(
        f"get_user_transfer_service_by_service_id() invoked : service_id {service_id}"
    )

    service_details = user_transfer_service_collection.find_one(
        {"_id": convert_to_object_id(service_id)}
    )

    if service_details:
        service_details = UserTransferServiceInternal(**service_details)

    log.info(f"get_user_transfer_service_by_service_id() returning : {service_details}")

    return service_details


def get_luggage_transfer_service_by_logistics_company_id(
    logistics_company_id: str,
) -> LuggageTransferServiceInternal:
    """return the luggage transfer service details by logistics company id

    Args:
        logistics_company_id (str)

    Returns:
        LuggageTransferServiceInternal
    """

    service_details = luggage_transfer_service_collection.find_one(
        {"provider.provider_id": logistics_company_id}
    )

    if service_details:
        service_details = LuggageTransferServiceInternal(**service_details)

    log.info(
        f"get_luggage_transfer_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details


def get_luggage_transfer_service_by_service_id(
    service_id: str,
) -> LuggageTransferServiceInternal:
    """return luggage transfer service details by service id

    Args:
        service_id (str)

    Returns:
        LuggageTransferServiceInternal
    """
    log.info(
        f"get_luggage_transfer_service_by_service_id() invoked : service_id {service_id}"
    )

    service_details = luggage_transfer_service_collection.find_one(
        {"_id": convert_to_object_id(service_id)}
    )

    if service_details:
        service_details = LuggageTransferServiceInternal(**service_details)

    log.info(
        f"get_luggage_transfer_service_by_service_id() returning : {service_details}"
    )

    return service_details


def get_all_services(
    collection: Collection,
):
    """return all the services for the given collection

    Args:
        collection (Collection)
    """
    log.info(f"get_all_services() invoked")
    return collection.find()


def get_all_club_to_club_services():
    """returns all the club to club services for all logistics company

    Returns:
        logistics company services for club to club transfer
    """
    log.info(f"get_all_club_to_club_services() invoked")
    return get_all_services(collection=club_to_club_service_collection)


def get_all_user_transfer_services():
    """returns all the user transfer services for all logistics company

    Returns:
        logistics company services for user transfer
    """
    log.info(f"get_all_user_transfer_services() invoked")
    return get_all_services(collection=user_transfer_service_collection)


def get_all_luggage_transfer_services():
    """returns all the luggage transfer services for all logistics company"""
    log.info("get_all_luggage_transfer_services() invoked")
    return get_all_services(collection=luggage_transfer_service_collection)
