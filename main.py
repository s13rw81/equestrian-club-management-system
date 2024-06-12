import uvicorn
from fastapi import FastAPI, Request

from api.auth import user_auth_router
from api.logistics import transfer_api_router, trucks_api_router
from api.user import user_api_router
from api.validators import validators_api_router
from config import DEBUG, HOST, PORT
from logging_config import log

app = FastAPI()

app.include_router(user_api_router)
app.include_router(user_auth_router)
app.include_router(validators_api_router)
app.include_router(transfer_api_router)
app.include_router(trucks_api_router)


@app.get("/")
async def root(request: Request):
    log.info(
        f"method: {request.method}, headers: {request.headers}, client: {request.client}"
    )
    return {"Hello": "World"}


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
