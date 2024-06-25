from data.db import get_horses_renting_service_collection
from pymongo.collection import Collection
from models.horse.horse_renting_service_internal import HorseRentingServiceInternal

collection: Collection = get_horses_renting_service_collection()


def create_horse_renting_service(horse_renting_service: HorseRentingServiceInternal):
    result = collection.insert_one(horse_renting_service.dict(by_alias=True))
    return str(result.inserted_id)


def get_renting_horse_by_id(horse_id: str):
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
