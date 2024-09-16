import uuid

import uvicorn
from fastapi import FastAPI, Request, status
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse

from api.auth import user_auth_router
from api.clubs.clubs_api import clubs_api_router
from api.horses.routers import horse_trade_services_router
from api.image_management import images_router
from api.logistics import logistics_admin_router, logistics_user_router
from api.onboarding import onboarding_api_router
from api.rbac_demo import demo_rbac_router
from api.riding_lesson_services.riding_lesson_services_api import (
    riding_lesson_services_api_router,
)
from api.upload_images_demo import upload_images_demo_router
from api.user import user_api_router
from api.validators import validators_api_router
from config import DEBUG, HOST, PORT
from logging_config import log

app = FastAPI()

app.include_router(onboarding_api_router)
app.include_router(riding_lesson_services_api_router)
app.include_router(clubs_api_router)
app.include_router(user_api_router)
app.include_router(user_auth_router)
app.include_router(validators_api_router)
app.include_router(demo_rbac_router)
app.include_router(logistics_admin_router)
app.include_router(images_router)
app.include_router(upload_images_demo_router)
app.include_router(logistics_user_router)
app.include_router(horse_trade_services_router)


# this exception handler will handle all the Exceptions
# except for FastAPI's HTTPException
# for HTTPExceptions the handler won't even get called
# not sure why :(
# but incidentally it's the expected behaviour anyway :)
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc):
    exception_id = uuid.uuid4().hex
    log.exception(
        f"[exception: {type(exc)}, assigned_id: {exception_id}] Something went wrong..."
    )
    exception_for_the_user = HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=f"something went wrong in our end [error_code: {exception_id}]",
    )
    return await http_exception_handler(request, exception_for_the_user)


@app.get("/", include_in_schema=False)
async def root(request: Request):
    log.info(
        f"method: {request.method}, headers: {request.headers}, client: {request.client}"
    )
    return {"status": "Hello World"}
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
