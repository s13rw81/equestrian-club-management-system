from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from data.dbapis.horse_selling_service.read_queries import (
    get_all_horse_sell_enquiries,
    get_horse_sell_listings,
    get_selling_enquiry_by_user_id,
)
from data.dbapis.horse_selling_service.write_queries import (
    add_horse_selling_service_details,
    add_horse_selling_service_enquiry,
    update_horse_selling_service_details,
    update_horse_selling_service_enquiry,
    update_selling_service_images,
)
from data.dbapis.horses.write_queries import add_horse, update_horse
from logging_config import log
from models.horse.horse import HorseInternal, UploadInfo
from models.horse.horse_selling_service_internal import (
    HorseSellingServiceEnquiryInternal,
    HorseSellingServiceInternal,
    Provider,
)
from utils.image_management import generate_image_urls, save_image

from .api_validators.horse_selling_service import (
    CreateSellEnquiryValidator,
    EnlistHorseForSellServiceValidator,
    GetHorseSellEnquiryValidator,
    GetHorseSellListingValidator,
    UpdateHorseForSellServiceListingValidator,
    UpdateSellEnquiryValidator,
    UploadSellImageValidator,
)
from .models import (
    CreateSellEnquiryResponse,
    EnlistHorseForSellResponse,
    GetHorseSellEnquiry,
    GetHorseSellListing,
)

horse_selling_service_router = APIRouter(prefix="", tags=["user-horses"])


@horse_selling_service_router.post(path="/enlist-for-sell")
def enlist_horse_for_sell(
    request: Request,
    payload: Annotated[EnlistHorseForSellServiceValidator, Depends()],
) -> EnlistHorseForSellResponse:

    user = payload.user
    enlist_details = payload.enlist_details

    log.info(f"{request.url.path} invoked enlist_details {enlist_details}")

    provider = UploadInfo(uploaded_by_id=user.id, uploaded_by_user=user.user_role)

    horse = HorseInternal(
        name=enlist_details.name,
        year_of_birth=enlist_details.year_of_birth,
        breed=enlist_details.breed,
        size=enlist_details.size,
        gender=enlist_details.gender,
        description=enlist_details.description,
        uploaded_by=provider,
    )

    horse_id = add_horse(horse_details=horse)

    if not horse_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to enlist horse for rent",
        )

    provider = Provider(provider_id=user.id, provider_type=user.user_role)
    selling_service_details = HorseSellingServiceInternal(
        horse_id=horse_id, provider=provider, price=enlist_details.price
    )

    selling_service_id = add_horse_selling_service_details(
        selling_service_details=selling_service_details
    )

    if not selling_service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to enlist horse for sell",
        )

    response = EnlistHorseForSellResponse(horse_selling_service_id=selling_service_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@horse_selling_service_router.post(path="/{horse_selling_service_id}/upload-images")
async def upload_sell_images(
    request: Request, payload: Annotated[UploadSellImageValidator, Depends()]
):

    files = payload.files
    service_id = payload.horse_selling_service_id
    log.info(f"{request.url.path} invoked horse_selling_service_id {service_id}")

    image_ids = []
    for file in files:
        image_id = await save_image(image_file=file)
        image_ids.append(image_id)

    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_selling_service_images(service_id=service_id, image_ids=image_ids)

    return {"status": "OK"}


@horse_selling_service_router.get(
    path="/get-horses-for-sell", response_model=List[GetHorseSellListing]
)
def get_horse_sell_listing(
    request: Request, payload: Annotated[GetHorseSellListingValidator, Depends()]
):
    user = payload.user
    own_listing = payload.own_listing
    log.info(f"{request.url.path} invoked ")

    sell_listings = get_horse_sell_listings(user_id=user.id, own_listing=own_listing)

    for sell_listing in sell_listings:
        sell_listing.image_urls = generate_image_urls(
            image_ids=sell_listing.image_urls, request=request
        )

    log.info(f"{request.url.path} returning {sell_listings}")

    return sell_listings


@horse_selling_service_router.put(
    path="/update-sell-listing/{horse_selling_service_id}"
)
def update_horse_selling_service_listings(
    request: Request,
    payload: Annotated[UpdateHorseForSellServiceListingValidator, Depends()],
):

    horse_selling_service_id = payload.horse_selling_service_id
    update_details = payload.update_details
    horse_id = payload.service_details.horse_id

    log.info(f"{request.url.path} invoked update_details {update_details}")

    update_horse(horse_id=horse_id, update_details=update_details.model_dump())

    update_horse_selling_service_details(
        service_id=horse_selling_service_id,
        update_details={
            "price": update_details.price,
            "updated_at": update_details.updated_at,
        },
    )

    return {"status": "OK"}


@horse_selling_service_router.post(path="/enquire-for-a-horse-sell")
def create_sell_enquiry(
    request: Request, payload: Annotated[CreateSellEnquiryValidator, Depends()]
) -> CreateSellEnquiryResponse:

    user = payload.user
    old_enquiry_details = payload.old_enquiry_details
    enquiry_details = payload.enquiry_details
    update_existing = payload.update_existing

    log.info(
        f"{request.url.path} invoked enquiry_details {enquiry_details}, old_enquiry_details {old_enquiry_details}"
    )

    if update_existing:
        update_horse_selling_service_enquiry(
            enquiry_id=old_enquiry_details.horse_selling_enquiry_id,
            enquiry_details=enquiry_details,
        )

        return CreateSellEnquiryResponse(
            horse_selling_enquiry_id=old_enquiry_details.enquiry_id
        )

    enquiry = HorseSellingServiceEnquiryInternal(
        user_id=user.id,
        horse_selling_service_id=enquiry_details.horse_selling_service_id,
        message=enquiry_details.message,
    )

    enquiry_id = add_horse_selling_service_enquiry(enquiry_details=enquiry)

    response = CreateSellEnquiryResponse(horse_selling_enquiry_id=enquiry_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@horse_selling_service_router.put(
    path="/update-horse-sell-enquiry/{horse_selling_enquiry_id}"
)
def update_sell_enquiry(
    request: Request, payload: Annotated[UpdateSellEnquiryValidator, Depends()]
):

    horse_sell_enquiry_id = payload.horse_sell_enquiry_id
    enquiry_details = payload.enquiry_details

    log.info(f"{request.url.path} invoked enquiry_details {enquiry_details}")

    update_horse_selling_service_enquiry(
        enquiry_id=horse_sell_enquiry_id, enquiry_details=enquiry_details
    )

    return {"status": "OK"}


@horse_selling_service_router.get(
    path="/get-horse-sell-enquiries", response_model=List[GetHorseSellEnquiry]
)
def get_sell_enquiries(
    request: Request,
    payload: Annotated[GetHorseSellEnquiryValidator, Depends()],
):

    is_admin = payload.is_admin
    user = payload.user
    log.info(f"{request.url.path} invoked")

    log.info(f"user_id {user.id}")

    if is_admin:
        response = get_all_horse_sell_enquiries()
    else:
        response = get_selling_enquiry_by_user_id(user_id=user.id)

    return response
