from bson import ObjectId
from data.db import async_get_clubs_collection


async def async_delete_club_by_id(club_id: str) -> str:
    clubs_collection = await async_get_clubs_collection()
    result = clubs_collection.delete_one({"_id": ObjectId(club_id)})
    return result.deleted_count == 1

