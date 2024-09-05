from data.dbapis.club_services_generic_activity.read_queries import get_existing_generic_activity_service_for_club
from data.dbapis.club_services_generic_activity.write_queries import insert_generic_activity_service_instance_to_club, \
    update_generic_activity_service, create_new_generic_activity_service_booking
from fastapi import HTTPException
from logging_config import log
from models.club_services_generic_activity.generic_activity_booking_model import GenericActivityBooking
from models.logistics_company_services import Provider
from models.club_services_generic_activity.generic_activity_service_model import GenericActivityService
from models.user import UserRoles
from starlette import status


def attach_generic_activity_service_to_club_logic(club_id: str, price: dict):
    log.info(f"attaching generic activity service to club with id {club_id} with price: {price}")

    # check if generic activity service already exists for club
    res = get_existing_generic_activity_service_for_club(club_id)
    if res:
        raise HTTPException(status_code = status.HTTP_303_SEE_OTHER, detail = 'generic activity serice already attached to club')

    # make a provider instance
    provider_instance = Provider(provider_id = club_id, provider_type = UserRoles.CLUB.value)

    # make a new generic activity service instance
    new_generic_service_instance = GenericActivityService(price = price['price'], provider = provider_instance)

    res = insert_generic_activity_service_instance_to_club(new_generic_service_instance)
    if res:
        msg = f'generic activity service attached to club {club_id}, res : {res.inserted_id}'
        log.info(msg)
        return msg


def update_generic_activity_service_by_club_id_logic(club_id, updated_club):
    # Convert the updated_club from pydantic model to dictionary
    updated_generic_activity_service_instance = updated_club.model_dump(exclude_none = True).get('generic_activity_service', None)
    if not updated_generic_activity_service_instance:
        return True

    # get the horse shoeing service associated with club
    existing_generic_activity_service = get_existing_generic_activity_service_for_club(club_id = club_id)


    updated_generic_activity_request = GenericActivityService(
        price = updated_generic_activity_service_instance['price'] if 'price' in updated_generic_activity_service_instance and updated_generic_activity_service_instance['price'] else existing_generic_activity_service['pricing_options'],
        provider = updated_generic_activity_service_instance['provider'] if 'provider' in updated_generic_activity_service_instance and updated_generic_activity_service_instance['provider'] else existing_generic_activity_service['provider'],
    )

    # Update the club in the database
    result = update_generic_activity_service(generic_activity_service_id = existing_generic_activity_service['id'], updated_generic_activity_service_instance = updated_generic_activity_request.model_dump())
    return result.modified_count == 1


def create_generic_activity_service_booking_logic(club_id: str, booking: dict, user_id: str):
    log.info(f'creating a booking for user {user_id} with club {club_id} for generic activity with details {booking}')

    generic_activity_service_id_for_club = get_existing_generic_activity_service_for_club(club_id=club_id)

    booking = GenericActivityBooking(
        user_id=user_id,
        generic_activity_service_id=generic_activity_service_id_for_club['id'],
        trainer_id=booking['trainer_id'],
        selected_date=booking['selected_date'],
        pricing_option=generic_activity_service_id_for_club['price'],
        number_of_visitors=booking['number_of_visitors']
    )
    result = create_new_generic_activity_service_booking(booking.model_dump())
    if result.inserted_id:
        return result.inserted_id
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail='error creating booking')

