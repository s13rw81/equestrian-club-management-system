from pydantic import BaseModel, field_validator
from typing import Any, Optional

class Lookup(BaseModel):
    from_collection: str
    local_field: str
    foreign_field: str
    as_key_name: str
    is_one_to_one: bool


class Filter(BaseModel):
    field_name: str
    operator: str
    value: Any

    @field_validator("operator")
    def validate_operator(cls, operator: str):
        stripped_operator = operator.strip()

        if stripped_operator not in ["gte", "lte", "eq", "in"]:
            raise ValueError("operator must be either one of the following: gte, lte, eq, in")

        return stripped_operator

class Sort(BaseModel):
    field_name: str
    operator: str

    @field_validator("operator")
    def validate_operator(cls, operator: str):
        stripped_operator = operator.strip()

        if stripped_operator not in ["asc", "desc"]:
            raise ValueError("operator must be either one of the following: asc, desc")

        return stripped_operator

class Pagination(BaseModel):
    page_no: int
    page_size: int

    @field_validator(
        "page_no",
        "page_size"
    )
    def ensure_positive_integer(cls, value):
        if value <= 0:
            raise ValueError("page_no or page_size must be positive integers...")

        return value


class GenericGetQueryWithPaginationDTO(BaseModel):
    lookups: Optional[list[Lookup]] = None
    filters: Optional[list[Filter]] = None
    sorts: Optional[list[Sort]] = None
    pagination: Optional[Pagination] = None