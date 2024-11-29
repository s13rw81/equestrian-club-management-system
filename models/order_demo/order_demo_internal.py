from ..common_base import CommonBase


class OrderDemoInternal(CommonBase):
    # user-fields
    service_name: str
    amount: str
    custom_data: list[str] = []
    payment_gateway_id: str
    payment_url: str
    payment_status: str
    club_id: str

    # system-fields
    user_id: str
    formatted_order_id: str