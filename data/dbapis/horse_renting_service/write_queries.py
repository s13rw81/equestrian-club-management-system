from data.db import get_horse_renting_service_collection
from logging_config import log
from models.horse.horse_renting_service_internal import HorseRentingServiceInternal

horse_renting_service_collection = get_horse_renting_service_collection()


def add_horse_renting_service_details(
    renting_service_details: HorseRentingServiceInternal,
) -> str:
    """given a horse_id create an entry for the horse in horse_renting_service collection and
    return the service_id

    Args:
        horse_id (str)
        renting_service_details (HorseRentingServiceInternal)

    Returns:
        str: id of the horse renting service
    """

    log.info(
        f"add_horse_renting_service_details() invoked renting_service_details {renting_service_details}"
    )

    renting_service_id = (
        horse_renting_service_collection.insert_one(
            renting_service_details.model_dump()
        )
    ).inserted_id

    log.info(f"add_horse_renting_service_details() returning {renting_service_id}")

    return str(renting_service_id)
