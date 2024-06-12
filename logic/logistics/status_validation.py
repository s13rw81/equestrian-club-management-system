from data.dbapis.transfer.read_queries import get_transfer_by_object_id
from logging_config import log
from models.transfer.enums import TransferStatus, TransferStatusPriority


def is_valid_update(transfer_id: str, status_to_update: TransferStatus) -> bool:
    """validates if the transfer with provided transfer_id can be updated
    to the provided status

    Args:
        transfer_id (str): transfer for which status should be update
        status_to_update (str): status to update to

    Returns:
        bool
    """

    log.info(
        f"inside is_valid_update : transfer_id {transfer_id} status_to_update {status_to_update}"
    )

    transfer_details = get_transfer_by_object_id(
        transfer_id=transfer_id, fields=["status"]
    )
    current_transfer_status = TransferStatus(transfer_details.get("status"))

    # def check_status_equality():
    #     return status_to_update == current_transfer_status

    # # this indicates that both the current and provided status are equal so no
    # # need to update
    # if check_status_equality:
    #     return False

    def check_valid_update():
        """status can only be updated to the next status.
        for eg. if the current status is 'in_transit' it would be
        wrong to update the transfer status to 'created' or 'cancelled'
        """

        current_status_priority = TransferStatusPriority[current_transfer_status.name]
        update_to_status_priority = TransferStatusPriority[status_to_update.name]

        log.info(f"current_status_priority {current_status_priority}")
        log.info(f"update_to_status_priority {update_to_status_priority}")

    check_valid_update()
