# All sorts of procedures, including data, logic and dtos are put in this file
# this is strictly for demonstration purposes. This structure should not be followed
# anywhere except for demonstration purposes.

from fastapi import APIRouter, Depends, Request, HTTPException, status
from logging_config import log
from pydantic import BaseModel, constr, field_validator
from decimal import Decimal
from role_based_access_control import RoleBasedAccessControl
from models.user import UserInternal
from models.user.enums import UserRoles
from models.order_demo import OrderDemoInternal, OrderDemoDetailedInternal
from data.dbapis.clubs import find_club
from data.db import get_order_demo_collection
from external_services.payment_gateway_service.models import CreatePaymentDTO, GetPaymentDTO
from external_services.payment_gateway_service.payment_gateway_service import create_payment_request, get_payment_info
from decorators import atomic_transaction
from typing import Optional
from logic.generic_get_query_with_pagination import generic_get_query_with_pagination_logic
from models.http_responses import Success


order_demo_collection = get_order_demo_collection()

class CreateOrderDTO(BaseModel):
    service_name: constr(min_length=1, max_length=1000)
    amount: Decimal
    custom_data: list[constr(min_length=1, max_length=10000)] = []
    club_id: str

    @field_validator("club_id")
    def validate_club_id(cls, club_id):
        result = find_club(id=club_id)

        if not result:
            log.info(f"invalid club_id = {club_id}, raising ValueError...")
            raise ValueError(f"invalid club_id = {club_id}")

        return club_id


order_demo_api_router = APIRouter(
    prefix="/order-demo",
    tags=["order-demo"]
)


@order_demo_api_router.post("/create-order")
async def create_order(
        request: Request,
        create_order_dto: CreateOrderDTO,
        user: UserInternal = Depends(
            RoleBasedAccessControl(allowed_roles={UserRoles.USER})
        )
):
    log.info(f"inside /order-demo/create-order (create_order_dto={create_order_dto}, "
             f"user_phone_number={user.phone_number}")

    result = create_order_demo_logic(
        request=request,
        create_order_dto=create_order_dto,
        user=user
    )

    retval = Success(
        message="demo order created successfully...",
        data=result
    )

    log.info(f"returning {retval}")

    return retval


@atomic_transaction
def create_order_demo_logic(
        request: Request,
        create_order_dto: CreateOrderDTO,
        user: UserInternal,
        session=None
):
    create_payment_dto = CreatePaymentDTO(
        amount=create_order_dto.amount,
        customer_name=user.full_name,
        customer_email="payment_demo@khayyal.com",
        payment_event_webhook=f"{request.base_url}payment-demo/verify-payment-status",
        redirect_url=f"{request.base_url}docs"
    )

    payment_info = create_payment_request(create_payment_dto=create_payment_dto)

    total_order_count = order_demo_collection.count_documents({})

    new_order_demo = OrderDemoInternal(
        service_name=create_order_dto.service_name,
        amount=create_order_dto.amount,
        custom_data=create_order_dto.custom_data,
        payment_gateway_id=payment_info.payment_gateway_id,
        payment_url=payment_info.payment_url,
        payment_status=payment_info.payment_status,
        club_id=create_order_dto.club_id,
        user_id=str(user.id),
        formatted_order_id=str(total_order_count).zfill(6)
    )

    result = order_demo_collection.insert_one(new_order_demo.model_dump(), session=session)

    if not result.acknowledged:
        log.info("failed to create demo order... raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="failed to create demo order"
        )

    retval = order_demo_get_query_with_pagination(
        f=[f"id$eq${new_order_demo.id}"],
        session=session
    )

    log.info(f"returning {retval}")

    return retval




@atomic_transaction
def order_demo_get_query_with_pagination(
        f: Optional[list[str]] = None,
        s: Optional[list[str]] = None,
        page_no: Optional[int] = None,
        page_size: Optional[int] = None,
        session=None
) -> list[OrderDemoDetailedInternal]:
    log.info("inside order_demo_get_query_with_pagination("
             f"f={f}, s={s}, page_no={page_no}, page_size={page_size})")

    result = generic_get_query_with_pagination_logic(
        primary_collection=get_order_demo_collection(),
        final_output_model=OrderDemoDetailedInternal,
        f=f, s=s, page_no=page_no, page_size=page_size, session=session
    )

    log.info(f"returning {result}")

    return result
