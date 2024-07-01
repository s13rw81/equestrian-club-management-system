from fastapi import HTTPException, APIRouter, status, Depends, UploadFile, File, Query, Request
from typing import List
from models.horse.horse_selling_service_internal import HorseSellingServiceInternal
from .models.horse_selling_service import HorseSellingItem, HorseSellingResponse
from data.dbapis.horses.horse_selling_service_queries import get_horse_by_id
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from models.horse.horse_internal import InternalSellHorse
from logic.auth import get_current_user
from models.user import UserInternal, UserRoles
from role_based_access_control import RoleBasedAccessControl
from bson import ObjectId
from data.db import get_horses_selling_service_collection, get_horses_collection, get_users_collection
from utils.image_management import save_image, generate_image_url
from utils.date_time import get_current_utc_datetime

def mask_email(email: str) -> str:
    if email and '@' in email:
        name, domain = email.split('@')
        return f"{name[0]}XXXXXXXXXX@{domain}"
    return email or "No Email"

def mask_phone(phone: str) -> str:
    if phone:
        return f"{phone[:3]}XXXXXXXXXX"
    return "No Phone"

# Get the horses collection
horses_collection = get_horses_collection()
horse_selling_service_collection = get_horses_selling_service_collection()
users_collection = get_users_collection()

horse_selling_service_api_router = APIRouter(
    prefix="/user/horses/get-horses-for-sale",
    tags=["horses_selling_services"]
)

@horse_selling_service_api_router.get("/{horse_id}", response_model=List[HorseSellingItem])
async def get_horses_selling(
    horse_id: str,
    user: UserInternal = Depends(RoleBasedAccessControl({UserRoles.ADMIN, UserRoles.USER})),
):
    horse = get_horse_by_id(horse_id)
    if horse:
        return JSONResponse(content=jsonable_encoder([horse]))  # Return a list containing the horse
    raise HTTPException(status_code=404, detail="Horse not found")

@horse_selling_service_api_router.post("/{horse_selling_service_id}/upload-images")
async def upload_image_demo(
    horse_selling_service_id: str,
    images: List[UploadFile] = File(...),
    user: UserInternal = Depends(RoleBasedAccessControl({UserRoles.ADMIN, UserRoles.USER})),
):
    # Check if the horse_selling_service_id belongs to the requesting user
    horse_service = horse_selling_service_collection.find_one({"_id": horse_selling_service_id})

    if horse_service is None:
        raise HTTPException(status_code=404, detail="Horse selling service not found")

    horse_id = horse_service["horse_id"]
    horse = horses_collection.find_one({"_id": horse_id})

    if horse is None:
        raise HTTPException(status_code=404, detail="Horse not found or you are not the owner")

    # Save images and collect their IDs
    image_ids = []
    for image in images:
        image_id = await save_image(image_file=image)  # Await the coroutine
        image_ids.append(image_id)

    # saving the image id in the database for later usages
    # caution: this is for demonstration purposes, database code should always be in data package



    # Update the horse document with image IDs
    if "images" not in horse:
        horse["images"] = image_ids
    else:
        horse["images"].extend(image_ids)

    if "images" not in horse_service:
        horse_service["images"] = image_ids
    else:
        horse_service["images"].extend(image_ids)

    horses_collection.update_one({"_id": horse_id}, {"$set": {"images": horse["images"]}})
    horse_selling_service_collection.update_one({"_id": horse_selling_service_id}, {"$set": {"images": horse_service["images"]}})

    return {"status": "OK"}

@horse_selling_service_api_router.get("/user/horses/get-horses-for-sell", response_model=List[HorseSellingResponse])
async def get_horses_for_sell(
    request: Request,  # Request parameter should be first
    own_listing: bool = Query(default=False),
    user: UserInternal = Depends(RoleBasedAccessControl({UserRoles.ADMIN, UserRoles.USER})),
):
    match_stage = {"$match": {"provider.provider_id": user.id}} if own_listing else {"$match": {"provider.provider_id": {"$ne": user.id}}}
    print("USER ID", user.id)

    pipeline = [
        match_stage,
        {
                '$lookup': {
                    'from': 'users',
                    'localField': 'provider_id',
                    'foreignField': '_id.oid',
                    'as': 'owner'
                }
            }, {
                '$unwind': '$owner'
            }, {
                '$project': {
                    'horse_selling_service_id': '$_id',
                    'horse_id': '$_id',
                    'name': '$name',
                    'year_of_birth': '$year_of_birth',
                    'breed': '$breed',
                    'size': '$size',
                    'gender': '$gender',
                    'description': '$description',
                    'images': '$images',
                    'price': '$price_sar',
                    'seller_information': {
                        'name': '$owner.full_name',
                        'email_address': mask_email("$owner.email_address"),
                        'phone_no': mask_phone("$owner.phone_number"),
                        'location': '$owner.address'
                    }
                }
            }
        ]

    result = list(horse_selling_service_collection.aggregate(pipeline))

    print(result)
    if not result:
        raise HTTPException(status_code=404, detail="No horses found")

    # Generate image URLs
    for horse in result:
        horse["image_urls"] = [generate_image_url(image_id, request) for image_id in horse.get("images", [])]
        del horse["images"]  # Remove the image IDs list since URLs are generated

    return result
