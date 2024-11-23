from models.trainers import TrainerDetailedInternal
from ..generic_get_query_with_pagination import generic_get_query_with_pagination_logic
from data.db import get_trainer_collection
from decorators import atomic_transaction
from typing import Optional
from logging_config import log


@atomic_transaction
def trainers_get_query_with_pagination(
        f: Optional[list[str]] = None,
        s: Optional[list[str]] = None,
        page_no: Optional[int] = None,
        page_size: Optional[int] = None,
        session=None
) -> list[TrainerDetailedInternal]:
    log.info("inside trainers_get_query_with_pagination("
             f"f={f}, s={s}, page_no={page_no}, page_size={page_size})")

    result = generic_get_query_with_pagination_logic(
        primary_collection=get_trainer_collection(),
        final_output_model=TrainerDetailedInternal,
        f=f, s=s, page_no=page_no, page_size=page_size, session=session
    )

    log.info(f"returning {result}")

    return result
