from data.db import get_horses_collection
from pymongo.collection import Collection
from models.horse.horse_internal import InternalHorse
collection: Collection = get_horses_collection()


def get_all_horses():
    horses = []
    for horse in collection.find():
        horses.append(InternalHorse(**horse))
    return horses


def get_horse_by_id(horse_id: str):
    horse = collection.find_one({"_id": horse_id})
    if horse:
        return InternalHorse(**horse)
    return None

