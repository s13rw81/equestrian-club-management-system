from bson import ObjectId
from data.db import get_clubs_collection

clubs_collection = get_clubs_collection()


def update_club(club_id: str, updated_club_request: dict):
    return clubs_collection.update_one({'_id': ObjectId(club_id)}, {'$set': updated_club_request})
