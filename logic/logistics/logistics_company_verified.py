from typing import Union

from data.dbapis.logistics.logistics_company.read_queries import (
    get_logistics_company_by_user_id,
)


def is_logistics_company_verified(user_id: str) -> Union[str, bool]:
    """returns the logistics_company_id if the logistics company is verified

    Args:
        user (UserInternal)

    Returns:
        bool
    """

    logistics_company_details = get_logistics_company_by_user_id(user_id=user_id)
    company_verified = logistics_company_details.get("is_khayyal_verified", None)

    return str(logistics_company_details.get("_id")) if company_verified else False
