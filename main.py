import uvicorn
from fastapi import FastAPI, Request
from config import log
app = FastAPI()


@app.get("/")
async def root(request: Request):
    log.info(f'method: {request.method}, headers: {request.headers}, client: {request.client}')
    return {"Hello": "World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=80, reload=True)
