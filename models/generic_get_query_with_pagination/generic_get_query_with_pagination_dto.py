from pydantic import BaseModel, field_validator, model_validator, ConfigDict, GetCoreSchemaHandler
from pydantic_core import CoreSchema
from pydantic._internal._model_construction import ModelMetaclass
from typing import Any, Optional, Union, Iterable, get_origin, get_args
from types import GenericAlias
from logging_config import log
from uuid import UUID


class Lookup(BaseModel):
    from_collection: str
    local_field: str
    foreign_field: str
    as_key_name: str
    is_one_to_one: bool

    # this code is to get rid of the checks of pydantic when an instantiation of this class
    # is used as metadata in Annotated
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
    :param filters: a list of dicts containing three fields: field_name, value, operator
    :param fields: {field_name: FieldInfo} dict of the final_output_model, can be obtained by using
    final_output_model.model_fields
    :return: a list of type checked dict conforming to the type of param `filters`
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
        type_checked_filter = type_check_ordinary_filter_predicate_wrapper(filter_predicate, fields)
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

    # FieldInfo.annotation returns the type of the field
    if not isinstance(field_info_former_field.annotation, ModelMetaclass):
        log.info("for nested filters, the type of the former field must be ModelMetaClass...")
        raise TypeError("for nested filters, the type of the former field must be ModelMetaClass("
                        f"filter_field_name={filter_field_name})")

    # type check the nested field
    nested_filter_type_checked = type_check_ordinary_filter_predicate_wrapper(
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


def type_check_ordinary_filter_predicate_wrapper(filter_predicate, fields):
    """
    This is a wrapper around the type_check_ordinary_filter_predicate to incorporate `in` operators.
    In cases of filter_predicates having an `in` operator, this function will verify whether the corresponding
    value is iterable firstly. And secondly whether each element in the iterable conform to the `type`.

    Otherwise, for filter_predicates that do to have the `in` operator, this function will serve as a proxy to the
    type_check_ordinary_filter_predicate function.

    :param filter_predicate: a dict containing three keys: field_name, value, operator
    :param fields: {field_name: FieldInfo} doct of the final_output_model, can be obtained by
    final_output_model.model_fields
    :return: a type-checked dict in the same form as the filter_predicate param
    """

    log.info(f"inside type_check_ordinary_filter_predicate_wrapper({filter_predicate}, {fields})")

    filter_operator = filter_predicate["operator"]
    filter_value = filter_predicate["value"]

    if filter_operator == "in":
        if not isinstance(filter_value, Iterable):
            log.info("when `in` operator is used, the filter_value must be an iterable... raising ValueError..")
            raise ValueError(f"filter_value: {filter_value} must be an iterable to ba compatible with `in` operator")

        type_checked_filter_predicates = [
            type_check_ordinary_filter_predicate(
                filter_predicate={
                    "field_name": filter_predicate["field_name"],
                    "operator": filter_operator,
                    "value": element
                },
                fields=fields
            )
            for element in filter_value
        ]

        filter_predicate["value"] = [
            type_checked_filter_predicate["value"] for type_checked_filter_predicate in type_checked_filter_predicates
        ]

        log.info(f"returning {filter_predicate}")

        return filter_predicate

    return type_check_ordinary_filter_predicate(filter_predicate, fields)

# applicable for filter predicates having non-nested field_name
def type_check_ordinary_filter_predicate(filter_predicate, fields):
    """
    This check is applicable for filter_predicates having non-nested field names e.g. field_name.
    This function checks whether the value in the filter_predicate conforms to the type of the corresponding
    field of the final_output_class. The type will primarily fall in three categories: 1. a non-iterable type e.g.
    str, int, float, 2. an iterable type, predominantly a list and 3. a Union type e.g. Union[int, None],
    Union[list[int], None]. Union types are rarely explicitly used in database models. However, Optional[int]
    is interpreted as Union[int, None] in the runtime.

    For a non-iterable type it simply attempts to cast the value in the filter_predicate to the associated type;
    a success in this operation implies conformity in the type and vice versa. (This operation is performed
    by a helper function.)

    For an iterable type it runs the same operation specified for a non-iterable type for each element of the
    iterable provided as a value. Post that, it casts the iterable into a list. A success in this chain of
    operations implies conformity in the type and vice versa. (This operation is performed by a helper function.)

    For a Union type, it extracts all the acceptable types, and runs the operations mentioned above, for the
    corresponding types i.e. iterable or non-iterable. NoneType is covered under non-iterable. (This operation
    is performed by a helper function)

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

    # FieldInfo.annotation returns the type of the field
    expected_field_type = field_info.annotation

    # being an instance of GenericAlias implies that the type is a list
    if isinstance(expected_field_type, GenericAlias):
        filter_field_value = type_check_or_coerce_list(expected_field_type, filter_field_value)

    # being an instance of type implies it's a primitive-like type e.g. str, int, float, None
    elif isinstance(expected_field_type, type):
        filter_field_value = type_check_or_coerce(expected_field_type, filter_field_value)

    # isinstance does not work on Union types
    # (get_origin(expected_type) is Union) works
    elif get_origin(expected_field_type) is Union:
        filter_field_value = type_check_or_coerce_union(expected_field_type, filter_field_value)

    else:
        log.info("the type of the field is not handled, raising TypeError...")

        raise TypeError("invalid type configuration")

    retval = {"field_name": filter_field_name, "operator": filter_operator, "value": filter_field_value}

    log.info(f"returning {retval}")

    return retval


def type_check_or_coerce_union(type_annotation, value):
    """
    This function takes a type_annotation that's a Union type. It checks whether the
    value conforms to the acceptable types of the union. If it doesn't, it attempts coercion.
    :param type_annotation: the expected type of the value, only Union types are handled
    :param value: the value that needs to be type checked or coerced
    :return: tye type checked or coerced value
    :raises ValueError in cases of failure in the operation
    :raises TypeError in cases it is provided a type that it does not support
    """
    log.info(f"inside type_check_or_coerce_a_union({type_annotation}, {value})")

    if get_origin(type_annotation) is not Union:
        log.info(f"provided type_annotation: {type_annotation} does not conform to type: Union, "
                 f"raising TypeError...")
        raise TypeError("invalid type configuration")

    acceptable_types = get_args(type_annotation)

    for acceptable_type in acceptable_types:

        if isinstance(acceptable_type, GenericAlias):

            log.info(f"acceptable_type={acceptable_type}, trying to coerce into a list...")

            try:
                return type_check_or_coerce_list(acceptable_type, value)
            except (TypeError, ValueError, Exception) as e:
                log.info(f"cannot coerce the value: {value} into a list, occurred exception: {e}, "
                         f"continuing on the loop...")

        elif isinstance(acceptable_type, type):

            log.info(f"acceptable_type={acceptable_type}, trying to coerce into a {acceptable_type}...")

            try:
                return type_check_or_coerce(acceptable_type, value)
            except (TypeError, ValueError, Exception) as e:
                log.info(f"cannot coerce the value: {value} into a {acceptable_type}, occurred exception: {e}")

    log.info(f"provided value: {value}, is incapable of being coerced into any of the acceptable_types: "
             f"{acceptable_types}, raising ValueError...")


def type_check_or_coerce_list(type_annotation, value):
    """
    This function takes a type_annotation that's of a list-like structure. It checks first whether the value is
    iterable, and finally, whether each element in the iterable conforms to the element type of the list-like
    structure. If the elements are not, it attempts coercion.
    :param type_annotation: the expected type of the value, only list-like structures are handled
    :param value: the value that needs to be type checked or coerced
    :return: the type checked or coerced value
    :raises ValueError in cases of failure in the operation
    :raises TypeError in cases it is provided a type that it does not support
    """
    log.info(f"inside type_check_or_coerce_a_list({type_annotation}, {value})")

    if not isinstance(type_annotation, GenericAlias):
        log.info(f"provided type_annotation: {type_annotation} does not conform to type: GenericAlias, "
                 f"raising TypeError...")
        raise TypeError("invalid type configuration")

    if not isinstance(value, Iterable):
        log.info(f"provided value: {value} is not Iterable... raising ValueError..")
        raise ValueError(f"provided value: {value} is not iterable...")

    element_type = get_args(type_annotation)[0]

    return [type_check_or_coerce(element_type, element) for element in value]


def type_check_or_coerce(type_annotation, value):
    """
    This function checks whether a value conforms to the type_annotation. In cases, it doesn't,
    the function attempts to coerce the value into the corresponding type; failure in which results in an
    exception being raised.
    :param type_annotation: the expected type of the value, only type instances (e.g. str, int, float) are handled
    :param value: the value that need to be type checked or coerced
    :return: the type checked or coerced value
    :raises ValueError in cases of failure in the operation
    :raises TypeError in cases it is provided a type that it does not support
    """

    log.info(f"inside type_check_or_coerce({type_annotation}, {value})")

    if not isinstance(type_annotation, type):
        log.info(f"provided type_annotation: {type_annotation} does not conform to type: type, "
                 f"raising TypeError...")
        raise TypeError("invalid type configuration")

    # since mongodb does not accept UUID instances, UUID values are cast into a string
    if type_annotation == UUID:
        type_annotation = str

    if isinstance(value, type_annotation):
        log.info(f"value: {value} conforms to the type: {type_annotation}, returning...")
        return value

    try:
        value = type_annotation(value)
        log.info(f"successfully coerced value: {value} into type: {type_annotation}, returning...")
        return value
    except (ValueError, Exception) as e:
        log.info(f"failed to coerce value: {value} into type: {type_annotation}, raising Exception...")
        raise ValueError(f"invalid value: {value}, when considered in the context of type: {type_annotation}")
