from models.generic_get_query_with_pagination import GenericGetQueryWithPaginationDTO
from decorators import atomic_transaction
from logging_config import log


# NOTE ON POTENTIAL PERFORMANCE OPTIMIZATION:
#  A possible way of performance improvement is to apply the filters before the lookups,
# thus limiting the number of documents for joins to be made. However, filters on fields which
# become available only after a lookup cannot be applied this way. To take advantage of this
# procedure, in filter predicates, there should be a way to differentiate between fields which
# belong to the primary collection and which become accessible only after the lookups; potentially
# passing the info from the logic layer through dtos.
@atomic_transaction
def generic_get_query_with_pagination(
        primary_collection,
        generic_get_query_dto: GenericGetQueryWithPaginationDTO,
        session=None
):
    log.info(f"inside generic_get_query_with_pagination(primary_collection={primary_collection}, "
             f"generic_get_query_dto={generic_get_query_dto})")

    pipeline = []

    # formulate all the lookup stages and unwind stages if applicable
    # and append it to the pipeline
    # if the DTO includes lookups
    if generic_get_query_dto.lookups:
        for lookup in generic_get_query_dto.lookups:
            lookup_stage = {
                "$lookup": {
                    "from": lookup.from_collection,
                    "localField": lookup.local_field,
                    "foreignField": lookup.foreign_field,
                    "as": lookup.as_key_name
                }
            }

            pipeline.append(lookup_stage)

            if lookup.is_one_to_one:
                unwind_stage = {
                    "$unwind": {
                        "path": f"${lookup.as_key_name}",
                        "preserveNullAndEmptyArrays": True
                    }
                }

                pipeline.append(unwind_stage)

    # formulate all the filter predicates
    # format the filter stage using the predicates
    # append the stage to the pipeline
    # if the DTO includes filters
    if generic_get_query_dto.filters:
        filter_dict = {}

        for filter_predicate in generic_get_query_dto.filters:
            filter_dict[filter_predicate.field_name] = {
                f"${filter_predicate.operator}": filter_predicate.value
            }

        pipeline.append({
            "$match": filter_dict
        })

    # formulate all the sort predicates
    # format the filter stage using the predicates
    # append the stage to the pipeline
    # if the DTO includes sorts
    if generic_get_query_dto.sorts:
        log.debug(f"sorts: {generic_get_query_dto.sorts}")

        sort_dict = {sort.field_name: 1 if sort.operator == "asc" else -1 for sort in generic_get_query_dto.sorts}

        pipeline.append({
            "$sort": sort_dict
        })

    # formulate skip and limit as per pagination requirements
    # append the stage to the pipeline
    # if the DTO includes pagination
    if generic_get_query_dto.pagination:
        pipeline.append({
            "$skip": (generic_get_query_dto.pagination.page_no - 1) * generic_get_query_dto.pagination.page_size
        })

        pipeline.append({
            "$limit": generic_get_query_dto.pagination.page_size
        })

    log.info(f"executing pipeline={pipeline}")

    database_cursor = primary_collection.aggregate(pipeline=pipeline, session=session)

    return database_cursor
