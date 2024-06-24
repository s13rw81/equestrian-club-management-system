from typing import Optional, List
from bson import ObjectId
from models.horse.horse_rent_internal import Horse
from data.db import get_horses_collection
from pymongo.collection import Collection
collection: Collection = get_horses_collection()

def horse_helper(horse) -> dict:
    return {
        "id": str(horse["_id"]),
        "name": horse["name"],
        "description": horse["description"],
        "year": horse["year"],
        "height": horse["height"],
        "club": horse["club"],
        "price": horse["price"],
        "image_url": horse["image_url"],
        "contact_option": horse["contact_option"],
        "for_sell": horse["for_sell"],
        "for_rent": horse["for_rent"],
        "available": horse.get("available", []),
    }

def search_horses_for_rent(
    search: Optional[str] = None,
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    date: Optional[str] = None,
    duration: Optional[str] = None,
) -> List[Horse]:
    query = {"for_rent": True}

    if search:
        query["$or"] = [
            {"name": {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}},
        ]
    if min_price is not None:
        query["price"] = {"$gte": min_price}
    if max_price is not None:
        query.setdefault("price", {})["$lte"] = max_price

    if date:
        query["available.date"] = date
    if duration:
        query["available.duration"] = duration

    horses = list(collection.find(query))
    return [horse_helper(horse) for horse in horses]

def contact_owner(id: str, date: str, duration: str) -> dict:
    horse = collection.find_one({"_id": ObjectId(id)})
    if not horse:
        return {"success": False, "message": "Horse not found"}

    contact_request = {
        "horse_id": ObjectId(id),
        "date": date,
        "duration": duration,
        "status": "pending",
    }
    result = db.contact_requests.insert_one(contact_request)
    if result.inserted_id:
        return {"success": True, "message": "Contact request sent", "item_id": str(result.inserted_id)}
    else:
        return {"success": False, "message": "Failed to send contact request"}
