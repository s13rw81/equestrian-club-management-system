from fastapi import APIRouter, Body, HTTPException, status, Request
from decimal import Decimal, InvalidOperation
from data.db import get_payment_demo_collection
from external_services.payment_gateway_service import create_payment_request, get_payment_info
from external_services.payment_gateway_service.models import GetPaymentDTO, CreatePaymentDTO
from logging_config import log
from models.http_responses import Success

payment_demo_router = APIRouter(
    prefix="/payment-demo",
    tags=["payment-demo"]
)

# putting the database code in the same file only for demonstration purposes
# data related code should always be in the data package
payment_demo_collection = get_payment_demo_collection()


@payment_demo_router.post("/create-payment")
def create_payment_demo(
        request: Request,
        amount: str = Body(...)
):
    log.info(f"inside /payment-demo/create-payment(amount={amount})")

    try:
        amount = Decimal(amount)
    except (InvalidOperation, Exception) as e:
        log.info(f"couldn't cast the provided amount into Decimal raising exception; exception={e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"provided amount={amount} is not a valid decimal value"
        )

    create_payment_dto = CreatePaymentDTO(
        amount=amount,
        customer_name="payment_demo",
        customer_email="payment_demo@khayyal.com",
        payment_event_webhook=f"{request.base_url}payment-demo/verify-payment-status",
        redirect_url=f"{request.base_url}docs"
    )

    payment_info = create_payment_request(create_payment_dto=create_payment_dto)

    # caution: this is only for demonstration purposes, database code should always be put in the data package
    payment_demo_collection.insert_one(payment_info.model_dump())

    return Success(
        message="payment url created successfully",
        data=payment_info
    )


@payment_demo_router.post("/verify-payment-status")
def verify_payment_status(
        id: str = Body(...)
):
    log.info(f"inside /payment-demo/verify-payment-status(id={id})")

    payment_info = get_payment_info(transaction_id=id)

    update_filter = {"payment_gateway_id": payment_info.payment_gateway_id}

    # caution: this is only for demonstration purposes, database code should always be put in the data package
    payment_demo_collection.update_one(
        update_filter,
        {"$set": {"payment_status": payment_info.payment_status}}
    )

    return Success(
        message="payment status updated successfully",
        data=payment_info
    )


@payment_demo_router.get("/get-all-payment-requests")
def get_all_payment_requests():
    log.info("inside /payment-demo/get-all-payment-requests")

    # caution: this is only for demonstration purposes, database code should always be put in the data package
    payments_cursor = payment_demo_collection.find()

    payments = [GetPaymentDTO(**payment) for payment in payments_cursor]

    log.info(f"returning {payments}")

    return Success(
        message="payments retrieved successfully",
        data=payments
    )