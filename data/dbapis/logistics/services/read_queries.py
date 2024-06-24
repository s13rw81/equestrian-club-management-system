from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.company import Company
from models.logistics.services import ClubToClubServiceInternal

logistics_company_collection = get_collection(collection_name="company")
logistics_service_club_to_club_collection = get_collection(
    collection_name="logistics_service_club_to_club"
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
            projection={"company_name": 1, "admin_id": 1},
        )
    except Exception as e:
        log.error(f"Exception : get_logistics_company_by_id {str(e)}")
        company_details = None

    log.info(f" company_details {company_details}")

    if company_details:
        company_details = Company(**company_details)

    log.info(f"get_logistics_company_by_id() returning : {company_details}")

    return company_details


def club_to_club_service_by_logistics_company_id(
    logistics_company_id: str,
) -> ClubToClubServiceInternal:
    """return club to club service details for the provided logistics_company_id

    Args:
        logistics_company_id (str)

    Returns:
        ClubToClubServiceInternal
    """

    log.info(
        f"club_to_club_service_by_logistics_company_id() invoked : logistics_company_id {logistics_company_id}"
    )

    try:
        service_details = logistics_service_club_to_club_collection.find_one(
            {"provider.provider_id": logistics_company_id}
        )
    except Exception as e:
        log.error(
            f"Exception : club_to_club_service_by_logistics_company_id() {str(e)}"
        )
        service_details = None

    log.info(f"service_details {service_details}")

    if service_details:
        service_details = ClubToClubServiceInternal(**service_details)

    log.info(
        f"club_to_club_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details


def get_club_to_club_service_by_service_id(
    service_id: str,
) -> ClubToClubServiceInternal:
    """return club to club service details by service id

    Args:
        service_id (str)

    Returns:
        ClubToClubServiceInternal
    """
    log.info(
        f"get_club_to_club_service_by_service_id() invoked : service_id {service_id}"
    )

    try:
        service_details = logistics_service_club_to_club_collection.find_one(
            {"_id": convert_to_object_id(service_id)}
        )
    except Exception as e:
        log.error(f"Exception : get_club_to_club_service_by_service_id() {str(e)}")
        service_details = None

    if service_details:
        service_details = ClubToClubServiceInternal(**service_details)

    log.info(
        f"club_to_club_service_by_logistics_company_id() returning : {service_details}"
    )

    return service_details
