import uvicorn
from api.auth import user_auth_router
from api.user import user_api_router
from api.validators import validators_api_router
from config import HOST, PORT, DEBUG
from fastapi import FastAPI, Request
from logging_config import log
from starlette.responses import RedirectResponse

app = FastAPI()

app.include_router(user_api_router)
app.include_router(user_auth_router)
app.include_router(validators_api_router)


@app.get("/", include_in_schema=False)
async def root(request: Request):
    log.info(f'method: {request.method}, headers: {request.headers}, client: {request.client}')
    return RedirectResponse(url='/docs')


if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
