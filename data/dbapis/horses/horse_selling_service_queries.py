from data.db import get_horses_collection, get_horses_selling_service_collection
from pymongo.collection import Collection
from models.horse.horse_selling_service_internal import HorseSellingServiceInternal

collection: Collection = get_horses_selling_service_collection()


def create_horse_selling_service(horse_selling_service: HorseSellingServiceInternal):
    result = collection.insert_one(horse_selling_service.dict(by_alias=True))
    return str(result.inserted_id)


def get_horse_by_id(horse_id: str):
    pipeline = [
        {"$match": {"horse_id": horse_id}},
        {"$project": {
            "_id": 1,
            "horse_id": 1,
            "provider": {
                "provider_id": "$provider.provider_id",
                "provider_type": "$provider.provider_type"
            },
            "price": "$price_sar"
        }}
    ]
    horse = list(collection.aggregate(pipeline))
    return horse[0] if horse else None
