from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from tibia import Tibia

import uvicorn

class Config(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

app = FastAPI()
config = Config()
tibia = Tibia()

@app.get("/tibia/news")
async def getTibiaNews():
    return tibia.getNews()

@app.get("/tibia/lastnew")
async def getTibiaLastNew():
    return tibia.getLastNew()

@app.get("/tibia/worlds")
async def getTibiaWorlds():
    return tibia.getWorlds()

if __name__ == "__main__":
    uvicorn.run(app, host=config.host, port=config.port)