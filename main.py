import uvicorn
from config import HOST, PORT, DEBUG
from fastapi import FastAPI, Request
from logging_config import log
app = FastAPI()


@app.get("/")
async def root(request: Request):
    log.info(f'method: {request.method}, headers: {request.headers}, client: {request.client}')
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=DEBUG)
