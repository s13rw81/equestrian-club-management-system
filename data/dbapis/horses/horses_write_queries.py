from data.db import get_horses_collection, get_horses_selling_service_collection
from pymongo.collection import Collection
from models.horse.horse_update_internal import InternalUpdateSellHorse
from api.horses.models.update_horse import HorseSellUpdate
from pymongo import ReturnDocument
collection: Collection = get_horses_collection()


def create_horse(horse: InternalUpdateSellHorse):
    # Insert the horse document into the collection
    result = collection.insert_one(horse.dict(by_alias=True))

    # Retrieve the inserted document's ID
    horse_id = result.inserted_id
    return str(horse_id)


# def update_horse(horse_id: str, horse_data: InternalUpdateSellHorse):
#     updated_horse = collection.find_one_and_update(
#         {"_id": horse_id},
#         {"$set": horse_data},
#         return_document=ReturnDocument.AFTER
#     )

#     if updated_horse:
#         return HorseSellUpdate(**updated_horse)
#     return None


def delete_horse(horse_id: str):
    delete_result = collection.delete_one({"_id": horse_id})
    return delete_result.deleted_count == 1


def update_horse(horse_id: str, horse_data: dict):
    updated_horse = collection.find_one_and_update(
        {"_id": horse_id},
        {"$set": horse_data},
        return_document=ReturnDocument.AFTER
    )
    if updated_horse:
        return updated_horse
    return None
