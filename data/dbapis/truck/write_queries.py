from typing import List

from data.db import convert_to_object_id, get_collection
from logging_config import log
from models.truck import TruckInternal

truck_collection = get_collection(collection_name="trucks")
company_collection = get_collection(collection_name="company")
club_to_club_service_collection = get_collection("logistics_service_club_to_club")
user_transfer_service_collection = get_collection("logistics_service_user_transfer")
user_transfer_with_insurance_service_collection = get_collection(
    "logistics_service_user_transfer_with_insurance"
)

SERVICE_COLLECTION_MAPPING = {
    "club_to_club": club_to_club_service_collection,
    "user_transfer": user_transfer_service_collection,
    "user_transfer_with_insurance": user_transfer_with_insurance_service_collection,
}


# TODO: Convert the below function to a transaction
def add_truck_db(truck: TruckInternal) -> bool:
    """adds a truck to the database.

    Args:
        truck (TruckInternal): truck to be added

    Returns:
        bool: if the truck was added successfully
    """

    def save_truck_db() -> str:
        """saves the new truck in the database and returns the id
        Returns:
            str: id
        """

        log.info(f"save_truck_db invoked : {truck}")
        insert_response = truck_collection.insert_one(truck.model_dump())

        truck_id, acknowledged = (
            str(insert_response.inserted_id),
            insert_response.acknowledged,
        )

        log.info(f"returning truck_id {truck_id} acknowledged {acknowledged}")

        return truck_id, acknowledged

    def update_truck_in_company_db(truck_id: str) -> bool:
        """add the new trucks reference to the company collection"""

        log.info(f"update_truck_in_company_db() ")

        filter = {"_id": convert_to_object_id(truck.logistics_company_id)}
        update_truck = {
            "$push": {
                "trucks": {
                    "truck_id": convert_to_object_id(truck_id),
                }
            }
        }

        update_response = company_collection.update_one(
            filter=filter, update=update_truck
        )

        log.info(
            f"update response {update_response.matched_count} {update_response.modified_count}"
        )

        return update_response.matched_count > 0

    def update_truck_in_service_collection(truck_id: str) -> bool:
        """add the new trucks reference to logistics company service collection"""

        log.info(f"update_truck_in_service_collection() ")

        filter = {"provider.provider_id": truck.logistics_company_id}
        update_service = {"$push": {"trucks": convert_to_object_id(truck_id)}}

        for service in truck.services:
            log.info(f"service {service}")

            collection = SERVICE_COLLECTION_MAPPING.get(service.value)
            collection.update_one(filter=filter, update=update_service)

        return

    def delete_truck(truck_id: str) -> bool:
        """delete the truck from the database with the provided truck_id

        Args:
            truck_id (str): the id of the truck to be deleted
        """
        filter = {"_id": convert_to_object_id(truck_id)}

        deleted = truck_collection.delete_one(filter=filter).deleted_count

        return deleted

    truck_id, acknowledged = save_truck_db()

    if not acknowledged:
        return False

    try:
        updated = update_truck_in_company_db(truck_id=truck_id)
        update_truck_in_service_collection(truck_id=truck_id)

    except Exception as e:
        log.error(f"error caught in update_truck_in_company_db() {str(e)}")

        delete_truck(truck_id=truck_id)

        return False

    return updated, truck_id


def update_truck_images(
    truck_id: str, file_paths: List[str], description: List[str]
) -> bool:
    """given a list of file_paths and a list of image descriptions update the same to truck
    collection

    Args:
        truck_id (str)
        file_paths (List[str])
        description (List[str])
    """

    log.info(f"update_truck_images() invoked : truck_id {truck_id}")

    image_data = [
        {"image_key": image_key, "description": description}
        for image_key, description in zip(file_paths, description)
    ]
    update = {"$set": {"images": image_data}}

    filter = {"_id": convert_to_object_id(truck_id)}
    updated = truck_collection.update_one(filter=filter, update=update)

    return updated.modified_count == 1


def update_truck_availability(truck_id: str, availability: str) -> bool:
    """given the truck_id update the availability of the truck

    Args:
        truck_id (str)
        availability (str)
    """

    log.info(f"update_truck_availability() invoke : {truck_id} {availability}")

    filter = {"_id": convert_to_object_id(truck_id)}
    update = {"$set": {"availability": availability}}

    updated = truck_collection.update_one(filter=filter, update=update)

    return updated.modified_count == 1
