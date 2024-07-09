from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.requests import Request

from data.dbapis.horse_renting_service.write_queries import (
    add_horse_renting_service_details,
    add_horse_renting_service_enquiry,
    update_horse_renting_service_details,
    update_renting_service_images,
)
from data.dbapis.horses.write_queries import add_horse, update_horse
from logging_config import log
from models.horse.horse import HorseInternal, UploadInfo
from models.horse.horse_renting_service_internal import (
    HorseRentingServiceEnquiryInternal,
    HorseRentingServiceInternal,
    Provider,
)
from utils.image_management import save_image

from .api_validators.horse_renting_service import (
    CreateRentEnquiryValidator,
    EnlistHorseForRentServiceValidator,
    UpdateHorseForRentServiceListingValidator,
    UploadRentImageValidator,
)
from .models import CreateRentEnquiryResponse, EnlistHorseForRentResponse

horse_renting_service_router = APIRouter(prefix="", tags=["user-horses"])


@horse_renting_service_router.post(path="/enlist-for-rent")
def enlist_horse_for_rent(
    request: Request,
    payload: Annotated[EnlistHorseForRentServiceValidator, Depends()],
) -> EnlistHorseForRentResponse:

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
    renting_service_details = HorseRentingServiceInternal(
        horse_id=horse_id, provider=provider, price_sar=enlist_details.price
    )

    renting_service_id = add_horse_renting_service_details(
        renting_service_details=renting_service_details
    )

    if not renting_service_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to enlist horse for rent",
        )

    response = EnlistHorseForRentResponse(horse_renting_service_id=renting_service_id)

    log.info(f"{request.url.path} returning {response}")

    return response


@horse_renting_service_router.post(
    path="/{horse_renting_service_id}/upload-rent-images"
)
async def upload_rent_images(
    request: Request, payload: Annotated[UploadRentImageValidator, Depends()]
):

    files = payload.files
    service_id = payload.horse_renting_service_id
    log.info(f"{request.url.path} invoked horse_renting_service_id {service_id}")

    image_ids = []
    for file in files:
        image_id = await save_image(image_file=file)
        image_ids.append(image_id)

    if not image_ids:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="unable to save image at this time",
        )

    update_renting_service_images(service_id=service_id, image_ids=image_ids)

    return {"status": "ok"}


@horse_renting_service_router.put(
    path="/update-rent-listing/{horse_renting_service_id}"
)
def update_horse_renting_service_listings(
    request: Request,
    payload: Annotated[UpdateHorseForRentServiceListingValidator, Depends()],
):

    horse_renting_service_id = payload.horse_renting_service_id
    update_details = payload.update_details
    horse_id = payload.service_details.horse_id

    log.info(f"{request.url.path} invoked update_details {update_details}")

    update_horse(horse_id=horse_id, update_details=update_details.model_dump())

    update_horse_renting_service_details(
        service_id=horse_renting_service_id,
        update_details={
            "price_sar": update_details.price,
            "updated_at": update_details.updated_at,
        },
    )

    return {"status": "ok"}


@horse_renting_service_router.post(path="/enquire-for-a-horse-rent")
def create_rent_enquiry(
    request: Request, payload: Annotated[CreateRentEnquiryValidator, Depends()]
) -> CreateRentEnquiryResponse:

    user = payload.user
    old_enquiry_details = payload.old_enquiry_details
    enquiry_details = payload.enquiry_details
    update_existing = payload.update_existing

    log.info(
        f"{request.url.path} invoked enquiry_details {enquiry_details}, old_enquiry_details {old_enquiry_details}"
    )

    if update_existing:
        # call the update enquiry function from here
        log.info("value of update_existing")
        return CreateRentEnquiryResponse(
            horse_renting_enquiry_id=old_enquiry_details.enquiry_id
        )

    enquiry = HorseRentingServiceEnquiryInternal(
        user_id=user.id,
        horse_renting_service_id=enquiry_details.horse_renting_service_id,
        message=enquiry_details.message,
        date=enquiry_details.date,
        duration=enquiry_details.duration,
    )

    enquiry_id = add_horse_renting_service_enquiry(enquiry_details=enquiry)

    response = CreateRentEnquiryResponse(horse_renting_enquiry_id=enquiry_id)

    log.info(f"{request.url.path} returning {response}")

    return response


# @horse_renting_service_router.put(
#     path="/update-horse-rent-enquiry/{horse_renting_enquiry_id}"
# )
# def update_rent_enquiry(
#     request: Request, payload: Annotated[UpdateRentEnquiryValidator, Depends()]
# ): ...
