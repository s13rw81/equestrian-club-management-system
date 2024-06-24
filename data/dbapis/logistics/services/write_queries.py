from api.logistics.models.services import UpdateClubToClubService
from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.logistics.services import ClubToClubServiceInternal

club_to_club_service_collection = get_collection(
    collection_name="logistics_service_club_to_club"
)


def save_club_to_club_service_db(service: ClubToClubServiceInternal) -> str:
    """saves the new service in the database and returns the id
    Returns:
        str: id
    """

    log.info(f"save_club_to_club_service_db() invoked : {service}")
    try:
        insert_response = club_to_club_service_collection.insert_one(
            service.model_dump()
        )
        service_id = str(insert_response.inserted_id)
    except Exception as e:
        log.error(f"Exception save_club_to_club_service_db() {str(e)}")
        service_id = None

    log.info(f"returning service_id {service_id}")

    return service_id


def update_club_to_club_service(
    service_id: str, update_details: UpdateClubToClubService
) -> bool:
    """updates the club to club service details in the database

    Args:
        service_id (str)
        update_details (dict)

    """

    log.info(
        f"update_club_to_club_service() invoked : service_id {service_id} update_details {update_details}"
    )

    try:
        update_response = club_to_club_service_collection.update_one(
            filter={"_id": convert_to_object_id(service_id)},
            update={
                "$set": {
                    "is_available": update_details.is_available.value,
                    "updated_at": update_details.updated_at,
                }
            },
        )
    except Exception as e:
        log.error(f"Exception : update_club_to_club_service() {str(e)}")
        return False

    log.info(
        f"matched_count={update_response.matched_count}, modified_count={update_response.modified_count}"
    )

    return update_response.modified_count == 1
