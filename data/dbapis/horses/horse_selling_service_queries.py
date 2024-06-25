from data.db import get_horses_selling_collection, get_horses_selling_service_collection
from pymongo.collection import Collection
from models.horse.horse_selling_service_internal import HorseSellingServiceInternal
from models.horse.horse_sell_internal import InternalSellHorse
from bson import ObjectId

collection: Collection = get_horses_selling_service_collection()

def create_horse_selling_service(horse_selling_service: HorseSellingServiceInternal):
    result = collection.insert_one(horse_selling_service.dict(by_alias=True))
    return str(result.inserted_id)


def get_horse_by_id(horse_id: str):
    pipeline = [
        {"$match": {"horse_id": horse_id}},
        {"$project": {
            "horse_id": "$horse_id",
            "provider_id": "$uploaded_by_id",
            "provider_type": "$uploaded_by_type",
            "price": "$price_sar",
        }}
    ]
    horse = list(collection.aggregate(pipeline))
    return horse[0] if horse else None
