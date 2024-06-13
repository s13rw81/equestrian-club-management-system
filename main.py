import uuid

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from starlette.responses import RedirectResponse

from api.auth import user_auth_router
from api.logistics import transfer_api_router, trucks_api_router
from api.user import user_api_router
from api.validators import validators_api_router
from config import DEBUG, HOST, PORT, status
from logging_config import log

app = FastAPI()

app.include_router(user_api_router)
app.include_router(user_auth_router)
app.include_router(validators_api_router)
app.include_router(transfer_api_router)
app.include_router(trucks_api_router)


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
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
