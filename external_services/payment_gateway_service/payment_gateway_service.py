from .models import CreatePaymentDTO, GetPaymentDTO
from fastapi import HTTPException, status
from config import TAP_PAYMENT_API_KEY, TAP_PAYMENT_API_URL
from logging_config import log
import requests

def create_payment_request(create_payment_dto: CreatePaymentDTO) -> GetPaymentDTO:
    log.info(f"inside create_payment_request(create_payment_dto={create_payment_dto})")

    request_data = {
        "amount": str(create_payment_dto.amount),
        "currency": "SAR",
        "customer": {
            "first_name": create_payment_dto.customer_name,
            "email": str(create_payment_dto.customer_email)
        },
        "source": {
            "id": "src_all"
        },
        "post": {
            "url": str(create_payment_dto.payment_event_webhook)
        },
        "redirect": {
            "url": str(create_payment_dto.redirect_url)
        }
    }

    request_endpoint = TAP_PAYMENT_API_URL + "/charges/"

    headers = {
        "Authorization": f"Bearer {TAP_PAYMENT_API_KEY}",
        "accept": "application/json",
        "content-type": "application/json"
    }

    log.info(f"making http call to create payment url; request_endpoint={request_endpoint}, "
             f"request_data={request_data}, headers={headers}")

    response = requests.post(request_endpoint, json=request_data, headers=headers)

    if response.status_code != 200:
        log.info(f"response status is not 200, raising exception; response_data={response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="unable to create payment url"
        )

    response_data = response.json()

    log.info(f"response={response_data}")

    retval = GetPaymentDTO(
        payment_gateway_id=response_data["id"],
        payment_url=response_data["transaction"]["url"],
        payment_status=response_data["status"]
    )

    log.info(f"returning {retval}")

    return retval


def get_payment_info(payment_gateway_id: str) -> GetPaymentDTO:
    log.info(f"inside get_payment_info(transaction_id={payment_gateway_id})")

    request_endpoint = TAP_PAYMENT_API_URL + f"/charges/{payment_gateway_id}"

    headers = {
        "Authorization": f"Bearer {TAP_PAYMENT_API_KEY}",
        "accept": "application/json"
    }

    log.info(f"making http request; request_endpoint={request_endpoint}, headers={headers}")
    response = requests.get(request_endpoint, headers=headers)

    if response.status_code != 200:
        log.info(f"response status code is not 200, raising exception; response={response.text}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="could not fetch details from payment gateway"
        )

    response_data = response.json()

    log.info(f"response={response_data}")

    retval = GetPaymentDTO(
        payment_gateway_id=response_data["id"],
        payment_url=response_data["transaction"].get("url"),
        payment_status=response_data["status"]
    )

    log.info(f"returning {retval}")

    return retval




