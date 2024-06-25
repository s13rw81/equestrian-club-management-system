from bson import ObjectId
from data.db import get_clubs_collection

clubs_collection = get_clubs_collection()


def delete_club_by_id_logic(club_id: str) -> str:
    result = clubs_collection.delete_one({"_id": ObjectId(club_id)})
    return result.deleted_count == 1
