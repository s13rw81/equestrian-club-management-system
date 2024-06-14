from bson import ObjectId
from data.db import get_horses_collection
from pymongo.collection import Collection

from api.horses.models.horse_data_models import Horse

collection: Collection = get_horses_collection()


def horse_helper(horse) -> dict:
    return {
        "id": str(horse["_id"]),
        "name": horse["name"],
        "description": horse["description"],
        "year": horse["year"],
        "height_cm": horse["height_cm"],
        "club_name": horse["club_name"],
        "price_sar": horse["price_sar"],
        "image_url": horse["image_url"],
        "contact_seller_url": horse["contact_seller_url"],
        "go_transport_url": horse["go_transport_url"],
    }


def get_all_horses():
    horses = []
    for horse in collection.find():
        horses.append(horse_helper(horse))
    return horses


def get_horse_by_id(horse_id: str):
    horse = collection.find_one({"_id": ObjectId(horse_id)})
    if horse:
        return horse_helper(horse)
    return None


def create_horse(horse: Horse):
    horse_id = collection.insert_one(horse.dict()).inserted_id
    new_horse = collection.find_one({"_id": horse_id})
    return horse_helper(new_horse)


def update_horse(horse_id: str, horse: Horse):
    updated_horse = collection.find_one_and_update(
        {"_id": ObjectId(horse_id)},
        {"$set": horse.dict()},
        return_document=True
    )
    if updated_horse:
        return horse_helper(updated_horse)
    return None


def delete_horse(horse_id: str):
    delete_result = collection.delete_one({"_id": ObjectId(horse_id)})
    return delete_result.deleted_count == 1
