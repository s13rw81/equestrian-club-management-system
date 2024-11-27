from typing import Optional

from data.db import get_clubs_collection
from decorators import atomic_transaction
from logging_config import log
from models.clubs.clubs_internal import ClubInternal

from ..generic_get_query_with_pagination import generic_get_query_with_pagination_logic


@atomic_transaction
def clubs_get_query_with_pagination(
    f: Optional[list[str]] = None,
    s: Optional[list[str]] = None,
    page_no: Optional[int] = None,
    page_size: Optional[int] = None,
    session=None,
) -> list[ClubInternal]:
    log.info(
        "inside clubs_get_query_with_pagination("
        f"f={f}, s={s}, page_no={page_no}, page_size={page_size})"
    )

    result = generic_get_query_with_pagination_logic(
        primary_collection=get_clubs_collection(),
        final_output_model=ClubInternal,
        f=f,
        s=s,
        page_no=page_no,
        page_size=page_size,
        session=session,
    )

    log.info(f"returning {result}")

    return result
