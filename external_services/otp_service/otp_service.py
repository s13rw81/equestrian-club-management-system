from logging_config import log
from fastapi.exceptions import HTTPException
from fastapi import status
import random
# from sendgrid import SendGridAPIClient
# from config import SENDGRID_API_KEY
# from sendgrid.helpers.mail import Mail, From, To


def generate_otp() -> str:
    return str(random.randrange(100000, 1000000))


def send_otp(email_address: str, first_name: str, last_name: str) -> str:
    """
        sends a randomly generated 6 digit OTP to
        the given email_address and returns the OTP back

        :param email_address: str
        :param first_name: first_name of the user
        :param last_name: last_name of the user
        :returns: the generated OTP
    """
    log.info(f"send_otp invoked: email_address={email_address}")
    otp = generate_otp()
    log.debug(f"GENERATED_OTP={otp}")

    # result = send_dynamic_email(
    #     to_email_address=email_address,
    #     first_name=first_name,
    #     last_name=last_name,
    #     otp=otp
    # )
    #
    # if not result:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="could not send otp email"
    #     )

    return otp


# TEMPLATE_ID = 'd-ef8e9b863e12470187e245428c264ed0'
#
#
# def send_dynamic_email(to_email_address: str, first_name: str, last_name: str, otp: str) -> bool:
#     logger.info(f"send_dynamic_email invoked: to_email_address={to_email_address}, "
#                 f"first_name={first_name}, last_name={last_name}")
#
#     message = Mail(
#         from_email=From(),
#         to_emails=To(to_email_address, f"{first_name} {last_name}")
#     )
#
#     # Set the dynamic template ID
#     message.template_id = TEMPLATE_ID
#
#     # TODO: replace the urls with proper urls
#     message.dynamic_template_data = {
#         "firstName": first_name,
#         "verifyEmailUrl": "",
#         "supportUrl": "",
#         "otp": otp,
#         "unsubscribe": ""
#     }
#
#     try:
#         sg = SendGridAPIClient(SENDGRID_API_KEY)
#         response = sg.send(message)
#
#         logger.info(f"email successfully send: status_code={response.status_code},"
#                     f"body={response.body}, headers={response.headers}")
#         return True
#     except Exception as e:
#         logger.exception(f"error occurred while sending the email: error={str(e)}")
#         return False
