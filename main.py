from fastapi import FastAPI
from config import log
app = FastAPI()


@app.get("/")
async def root():
    log.info('')
    return {"Hello": "World"}
