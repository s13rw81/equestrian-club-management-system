from typing import Dict

from data.db import get_logistics_company_collection
from logging_config import log

logistics_company_collection = get_logistics_company_collection()


def get_logistics_company_by_user_id(user_id: str) -> Dict:
    """based on user_id return the logistics company to which the
    user belongs to

    Args:
        user_id (str)

    Returns:
        Dict
    """

    log.info(f"get_logistics_company_by_user_id() invoked user_id:{user_id}")

    filter = {"users.user_id": user_id}
    projection = {"is_khayyal_verified": True, "trucks": True}
    logistics_company = logistics_company_collection.find_one(
        filter=filter, projection=projection
    )

    log.info(f"get_logistics_company_by_user_id() returning {logistics_company}")

    return logistics_company
