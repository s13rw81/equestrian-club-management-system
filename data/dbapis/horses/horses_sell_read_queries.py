from data.db import get_horses_selling_collection
from pymongo.collection import Collection
from models.horse.horse_sell_internal import InternalSellHorse
collection: Collection = get_horses_selling_collection()


def get_all_horses():
    horses = []
    for horse in collection.find():
        horses.append(InternalSellHorse(**horse))
    return horses


def get_horse_by_id(horse_id: str):
    horse = collection.find_one({"_id": horse_id})
    if horse:
        return InternalSellHorse(**horse)
    return None
