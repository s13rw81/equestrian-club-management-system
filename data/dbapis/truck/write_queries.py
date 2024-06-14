from typing import List

from data.db import convert_to_object_id, get_company_collection, get_truck_collection
from logging_config import log
from models.truck import TruckInternal

truck_collection = get_truck_collection()
company_collection = get_company_collection()


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

    def update_truck_in_company_db(truck_id: str) -> str:
        """add the new trucks reference to the company collection"""

        log.info(f"update_truck_in_company_db() ")

        filter = {"_id": convert_to_object_id(truck.company_id)}
        update_truck = {
            "$push": {
                "trucks": {
                    "truck_id": truck.model_dump(),
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

    except Exception as e:
        log.error(f"error caught in update_truck_in_company_db() ")

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
