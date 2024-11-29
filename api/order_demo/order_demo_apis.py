# All sorts of procedures, including data, logic and dtos are put in this file
# this is strictly for demonstration purposes. This structure should not be followed
# anywhere except for demonstration purposes.

from fastapi import (
    APIRouter,
    Depends,
    Request,
    HTTPException,
    status,
    Body,
    Query
)
from logging_config import log
from pydantic import BaseModel, constr, field_validator
from decimal import Decimal, InvalidOperation
from role_based_access_control import RoleBasedAccessControl
from models.user import UserInternal
from models.user.enums import UserRoles
from models.order_demo import OrderDemoInternal, OrderDemoDetailedInternal
from data.dbapis.clubs import find_club
from data.db import get_order_demo_collection
from external_services.payment_gateway_service.models import CreatePaymentDTO, GetPaymentDTO
from external_services.payment_gateway_service.payment_gateway_service import create_payment_request, get_payment_info
from decorators import atomic_transaction
from typing import Optional, Annotated
from logic.generic_get_query_with_pagination import generic_get_query_with_pagination_logic
from models.http_responses import Success
from ..commons.models import GetQueryPaginatedDTO

order_demo_api_router = APIRouter(
    prefix="/order-demo",
    tags=["order-demo"]
)

order_demo_collection = get_order_demo_collection()


class CreateOrderDTO(BaseModel):
    service_name: constr(min_length=1, max_length=1000)
    amount: str
    custom_data: list[constr(min_length=1, max_length=10000)] = []
    club_id: str

    @field_validator("club_id")
    def validate_club_id(cls, club_id):
        result = find_club(id=club_id)

        if not result:
            log.info(f"invalid club_id = {club_id}, raising ValueError...")
            raise ValueError(f"invalid club_id = {club_id}")

        return club_id

    @field_validator("amount")
    def validate_amount(cls, amount):
        try:
            Decimal(amount)
        except (InvalidOperation, Exception) as e:
            log.info("couldn't convert amount into a Decimal...")
            log.exception(e)
            log.info("raising ValueError...")
            raise ValueError("couldn't convert amount into a Decimal...")

        return amount


@order_demo_api_router.post("/create-order")
async def create_order(
        request: Request,
        create_order_dto: CreateOrderDTO,
        user: Annotated[UserInternal, Depends(
            RoleBasedAccessControl(allowed_roles={UserRoles.USER})
        )]
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


@order_demo_api_router.post("/update-payment-status")
async def verify_payment_status(
        user: Annotated[UserInternal, Depends(
            RoleBasedAccessControl(allowed_roles={UserRoles.USER})
        )],
        order_id: str = Body(embed=True)
):
    log.info(f"inside /order-demo/verify-payment-status (order_id={order_id}, user_phone_number={user.phone_number})")

    order_demo = order_demo_collection.find_one({"id": order_id})

    if not order_demo:
        log.info("invalid order_id, raising ValueError...")
        raise ValueError(f"invalid order_id: {order_id}")

    if order_demo["user_id"] != str(user.id):
        log.info("user is not authorized to access this order... raising ValueError...")
        raise ValueError(f"user is not authorized to access this order: {order_id}")

    result = update_payment_status_logic(order_id=order_id)

    retval = Success(
        message="successfully update payment status...",
        data=result
    )

    log.info(f"returning {retval}")

    return retval


@atomic_transaction
def update_payment_status_logic(
        order_id: str,
        session=None
):
    log.info(f"inside update_payment_status_logic(order_id={order_id})")

    order_demo = order_demo_collection.find_one({"id": order_id}, session=session)

    payment_info = get_payment_info(payment_gateway_id=order_demo["payment_gateway_id"])

    result = order_demo_collection.update_one(
        {"id": order_id},
        {"$set": {"payment_status": payment_info.payment_status}},
        session=session
    )

    if not result.modified_count:
        log.info("unable to update payment status... raising HTTPException...")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to update payment status..."
        )

    retval = order_demo_get_query_with_pagination(
        f=[f"id$eq${order_id}"],
        session=session
    )

    log.info(f"returning {retval}")

    return retval


@order_demo_api_router.post("/get-orders-paginated")
def get_orders_paginated_logic(
        get_query_paginated_dto: Annotated[GetQueryPaginatedDTO, Query()],
        user: Annotated[UserInternal, Depends(
            RoleBasedAccessControl(allowed_roles={UserRoles.USER})
        )]
):
    f = get_query_paginated_dto.f
    s = get_query_paginated_dto.s
    page_no = get_query_paginated_dto.page_no
    page_size = get_query_paginated_dto.page_size

    log.info(f"inside /order-demo/get-orders-paginated (f={f}, s={s}, page_no={page_no}, page_size={page_size}, "
             f"user_phone_number={user.phone_number})")

    f = f + [f"user_id$eq${user.id}"] if f else [f"user_id$eq${user.id}"]

    result = order_demo_get_query_with_pagination(
        f=f, s=s, page_no=page_no, page_size=page_size
    )

    retval = Success(
        message="demo orders fetched successfully...",
        data=result
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
