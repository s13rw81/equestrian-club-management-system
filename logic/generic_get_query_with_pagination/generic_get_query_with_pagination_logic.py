from models.generic_get_query_with_pagination import (
    GenericGetQueryWithPaginationDTO,
    Filter,
    Sort,
    Pagination
)
from data.dbapis.generic_get_query_with_pagination import generic_get_query_with_pagination
from decorators.atomic_transaction import atomic_transaction
from logging_config import log
from typing import Optional
import re
from fastapi import HTTPException, status


@atomic_transaction
def generic_get_query_with_pagination_logic(
        primary_collection,
        final_output_model,
        f: Optional[list[str]] = None,
        s: Optional[list[str]] = None,
        page_no: Optional[int] = None,
        page_size: Optional[int] = None,
        session=None
):
    log.info("inside generic_get_query_with_pagination_logic("
             f"final_output_model={final_output_model}, "
             f"f={f}, "
             f"s={s}, "
             f"page_no={page_no}, "
             f"page_size={page_size})")

    s = s + ["id$asc"] if s else ["id$asc"]

    generic_get_query_dto = GenericGetQueryWithPaginationDTO(
        final_output_model=final_output_model,
        filters=format_filter_strings(filter_strings=f) if f else None,
        sorts=format_sort_strings(sort_strings=s),
        pagination=Pagination(
            page_no=page_no,
            page_size=page_size
        ) if page_no else None
    )

    database_cursor = generic_get_query_with_pagination(
        primary_collection=primary_collection,
        generic_get_query_dto=generic_get_query_dto,
        session=session
    )

    retval = [final_output_model(**data) for data in database_cursor]

    log.info(f"returning {retval}")

    return retval


def format_filter_strings(filter_strings: list[str]) -> list[Filter]:
    log.info(f"inside format_filter_strings(filter_strings={filter_strings})")

    formatted_filters = []

    for filter_string in filter_strings:

        filter_string = filter_string.strip()

        filter_splitted = filter_string.split("$")

        if len(filter_splitted) != 3:
            log.info("invalid filter elements length, "
                     "a filter string must have three elements separated by '$': the field_name, the operator, "
                     f"and the value (filter_string={filter_string})")

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="invalid filter elements length, "
                       "a filter string must have three elements separated by '$': "
                       f"the field_name, the operator, and the value (filter_string={filter_string})"
            )

        field_name_regex = r'[\w.]+'

        if not re.fullmatch(field_name_regex, filter_splitted[0]):
            log.info("only alphanumeric characters, underscores, and a single dot are allowed as a "
                     f"filter field name (filter_field_name={filter_splitted[0]})")

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="only alphanumeric characters, underscores, and a single dot are allowed as a "
                       f"filter field name (filter_field_name={filter_splitted[0]})"
            )

        formatted_filter = Filter(
            field_name=filter_splitted[0],
            operator=filter_splitted[1],
            value=filter_splitted[2].split("~") if filter_splitted[1] == "in" else filter_splitted[2]
        )

        formatted_filters.append(formatted_filter)

    log.info(f"returning {formatted_filters}")

    return formatted_filters


def format_sort_strings(sort_strings: list[str]) -> list[Sort]:
    log.info(f"inside format_sort_strings(sort_strings={sort_strings})")

    formatted_sorts = []

    for sort_string in sort_strings:
        sort_string = sort_string.strip()

        sort_splitted = sort_string.split("$")

        if len(sort_splitted) != 2:
            log.info("invalid sort elements length, "
                     "a sort string must have only two elements separated by '$': the field_name and the operator "
                     f"(sort_string={sort_string})")

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="invalid sort elements length, "
                       "a sort string must have only two elements separated by '$': the field_name and the operator "
                       f"(sort_string={sort_string})"
            )

        field_name_regex = r'[\w\.]+'

        if not re.fullmatch(field_name_regex, sort_splitted[0]):
            log.info("only alphanumeric characters, underscores, and a single dot are allowed as a "
                     f"sort field name (sort_field_name={sort_splitted[0]})")

            raise HTTPException(
                status_code=status.HTTP_406_NOT_ACCEPTABLE,
                detail="only alphanumeric characters, underscores, and a single dot are allowed as a "
                       f"sort field name (sort_field_name={sort_splitted[0]})"
            )

        formatted_sort = Sort(
            field_name=sort_splitted[0],
            operator=sort_splitted[1]
        )

        formatted_sorts.append(formatted_sort)

    log.info(f"returning {formatted_sorts}")

    return formatted_sorts
