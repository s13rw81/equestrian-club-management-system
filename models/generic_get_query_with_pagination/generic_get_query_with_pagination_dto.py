from pydantic import BaseModel, field_validator, model_validator, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any, Optional
from types import GenericAlias
from logging_config import log
from uuid import UUID


class Lookup(BaseModel):
    from_collection: str
    local_field: str
    foreign_field: str
    as_key_name: str
    is_one_to_one: bool

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type[BaseModel], handler: GetCoreSchemaHandler) -> CoreSchema:
        if cls is not source_type:
            return handler(source_type)
        return super().__get_pydantic_core_schema__(source_type, handler)


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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    final_output_model: ModelMetaclass
    lookups: Optional[list[Lookup]] = None
    filters: Optional[list[Filter]] = None
    sorts: Optional[list[Sort]] = None
    pagination: Optional[Pagination] = None

    @model_validator(mode="before")
    def extract_lookups_and_run_type_checks(cls, data: Any) -> Any:
        if isinstance(data, dict):
            final_output_model = data["final_output_model"]

            fields = final_output_model.model_fields

            # extract the lookup objects from fields tha are annotated
            lookups = [field_info.metadata[0] for field_info in fields.values() if field_info.metadata]
            data["lookups"] = lookups

            # perform type checks on all the filter data
            if data.get("filters"):
                data["filters"] = type_check_filters(data["filters"], fields)

            if data.get("sorts"):
                field_name_check_sorts(data["sorts"], fields)


        return data


def field_name_check_sorts(sorts, fields):

    """
    Checks the accuracy of the field_names in the sort directives. For non-nested fields,
    it simply checks for the existence of the field in the `fields`. Otherwise, it affirms
    the former field being of type `ModelMetaClass` and the nested fields exists in the model_fields
    of the corresponding `ModelMetaClass`.
    :param sorts: list of dicts having 2 keys: field_name, operator
    :param fields: list[{field_name: FieldInfo}] of the final_output_model, can be obtained by
    final_output_model.model_fields
    :return: True in case the validation succeeds, otherwise raises ValueError or TypeError depending upon
    the circumstances
    """

    log.info(f"inside field_name_check_sorts(sorts={sorts}, fields={fields})")

    sorts = [sort.model_dump() for sort in sorts]

    for sort in sorts:
        field_name = sort["field_name"]

        # for nested fields e.g. field_name.nested_field
        if "." in field_name:
            sort_field_names = field_name.split(".")

            if len(sort_field_names) != 2:
                log.info(f"only one level of nesting is allowed in sorts(field_name={field_name})")
                raise ValueError(f"only one level of nesting is allowed in sorts(field_name={field_name})")

            former_field_info = fields.get(sort_field_names[0])

            if not former_field_info:
                log.info(f"invalid field name (field_name={field_name})")
                raise ValueError(f"invalid field name (field_name={field_name})")

            if not isinstance(former_field_info.annotation, ModelMetaclass):
                log.info("for nested sorts, the type of the former field must be of type MetaModelClass, "
                         f"(field_name={sort_field_names[0]})")
                raise TypeError("for nested sorts, the type of the former field must be of type MetaModelClass, "
                                f"(field_name={sort_field_names[0]})")

            if not sort_field_names[1] in former_field_info.annotation.model_fields:
                log.info(f"invalid nested field_name={sort_field_names[1]}")
                raise ValueError(f"invalid field_name={field_name}")

        else:
            if not field_name in fields:
                log.info(f"invalid field_name (field_name={field_name})")
                raise ValueError(f"invalid field_name (field_name={field_name})")

    return True


def type_check_filters(filters, fields):
    """
    Type checks all the filters by using either `type_check_ordinary_filter_predicate` or
    `type_check_nested_filter_predicate`
    :param filters: a list of dict containing three fields: field_name, value, operator
    :param fields: {field_name: FieldInfo} dict of the final_output_model, can be obtained by using
    final_output_model.model_class
    :return: a list of typed checked dict conforming to the type of param `filters`
    """
    log.info(f"inside type_check_filters(filters={filters}, fields={fields})")

    filters = [filter_predicate.model_dump() for filter_predicate in filters]

    type_checked_filters = []

    nested_filter_predicates = []

    ordinary_filter_predicates = []

    for filter_predicate in filters:
        if "." in filter_predicate["field_name"]:
            nested_filter_predicates.append(filter_predicate)
        else:
            ordinary_filter_predicates.append(filter_predicate)

    for filter_predicate in ordinary_filter_predicates:
        type_checked_filter = type_check_ordinary_filter_predicate(filter_predicate, fields)
        type_checked_filters.append(type_checked_filter)

    for filter_predicate in nested_filter_predicates:
        type_checked_nested_filter = type_check_nested_filter_predicates(filter_predicate, fields)
        type_checked_filters.append(type_checked_nested_filter)

    log.info(f"returning {type_checked_filters}")

    return type_checked_filters


# applicable for filter_predicates where field name is of the pattern: field_name.nested_field_name
def type_check_nested_filter_predicates(filter_predicate, fields):
    """
    The check is applicable for filter_predicates having nested field names e.g. field_name.nested_field_name.
    For the former field name (field on the left side of the dot notation) it checks whether it conforms to type
    ModelMetaClass, and for the latter it runs the type check for the value using the
    `type_check_ordinary_filter_predicate function`.

    :param filter_predicate: a dict containing three keys: field_name, value, operator
    :param fields: {field_name: FieldInfo} dict of the final_output_model,
    can be obtained by final_output_model.model_fields
    :return: a typed checked dict in the same form as the filter_predicate param
    """

    log.info(f"inside type_check_nested_filter_predicates(filter_predicate={filter_predicate}, "
             f"fields={fields})")

    filter_field_name = filter_predicate["field_name"]
    filter_field_value = filter_predicate["value"]
    filter_operator = filter_predicate["operator"]

    filter_field_names = filter_field_name.split(".")

    if len(filter_field_names) != 2:
        log.info("nested filter predicate does not have two elements, raising ValueError")
        raise ValueError(f"only one level of nesting is allowed, filter_field_name={filter_field_name}")

    field_info_former_field = fields.get(filter_field_names[0])

    if not field_info_former_field:
        log.info(f"invalid filter_field_name={filter_field_name}")
        raise ValueError(f"invalid filter_field_name={filter_field_name}")

    if not isinstance(field_info_former_field.annotation, ModelMetaclass):
        log.info("for nested filters, the type of the former field must be ModelMetaClass...")
        raise TypeError("for nested filters, the type of the former field must be ModelMetaClass("
                        f"filter_field_name={filter_field_name})")

    # type check the nested field
    nested_filter_type_checked = type_check_ordinary_filter_predicate(
        filter_predicate={
            "field_name": filter_field_names[1],
            "operator": filter_operator,
            "value": filter_field_value
        },
        fields=field_info_former_field.annotation.model_fields
    )

    retval = {
        "field_name": filter_field_name,
        "operator": filter_operator,
        "value": nested_filter_type_checked["value"]
    }

    log.info(f"returning {retval}")

    return retval


# applicable for filter predicates having non-nested field_name
def type_check_ordinary_filter_predicate(filter_predicate, fields):
    """
    This check is applicable for filter_predicates having non-nested field names e.g. field_name.
    This function checks whether the value in the filter_predicate conforms to the type of the corresponding
    field of the final_output_class. The type will primarily fall in two categories: 1. a non-iterable type e.g.
    str, int, float and 2. an iterable type predominantly list.

    For a non-iterable type it simply attempts to cast the value in the filter_predicate to the associated type;
    a success in this operation implies conformity in the type and vice versa.

    For an iterable type it runs the same operation specified for a non-iterable type for each element of the
    iterable provided as a value. Post that, it casts the iterable into a list. A success in this chain of
    operations implies conformity in the type and vice versa.

    :param filter_predicate: a dict containing three keys: field_name, value, operator
    :param fields: {field_name: FieldInfo} dict of the final_output_model,
    can be obtained by final_output_model.model_fields
    :return: a type-checked dict in the same form as the filter_predicate param
    """
    log.info(f"inside type_check_ordinary_filter_predicate(filter_predicate={filter_predicate},"
             f"fields={fields})")

    filter_field_name = filter_predicate["field_name"]
    filter_field_value = filter_predicate["value"]
    filter_operator = filter_predicate["operator"]

    field_info = fields.get(filter_field_name)

    if not field_info:
        log.info(f"invalid filter_field_name={filter_field_name}")
        raise ValueError(f"invalid filter_field_name={filter_field_name}")

    # being an instance of GenericAlias implies that the type is a list
    if isinstance(field_info.annotation, GenericAlias):
        # .__args__[0] on GenericAlias returns the value type of the list
        value_type = field_info.annotation.__args__[0]

        if value_type == UUID:
            value_type = str

        try:
            filter_field_value = list(map(value_type, filter_field_value))
        except (TypeError, Exception) as e:
            log.exception(f"occurred exception = {e}")
            raise ValueError(f"invalid filter_value (filter_field={filter_field_name}, "
                             f"filter_field_value={filter_field_value})")

    elif isinstance(field_info.annotation, type):
        value_type = field_info.annotation
        if value_type == UUID:
            value_type = str
        try:
            filter_field_value = value_type(filter_field_value)
        except (ValueError, Exception) as e:
            log.exception(f"occurred exception = {e}")
            raise ValueError(f"invalid filter_value (field_field={filter_field_name}, "
                             f"filter_field_value={filter_field_value})")

    else:
        log.info("the type of the field is not handled, raising TypeError...")
        raise TypeError("invalid type configuration")

    retval = {"field_name": filter_field_name, "operator": filter_operator, "value": filter_field_value}

    log.info(f"returning {retval}")

    return retval
