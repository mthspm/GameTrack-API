from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from tibia import Tibia

import uvicorn

class Config(BaseModel):
    title: str = "GAMETRACK API"
    description : str = "API that tracks data from games"
    version : str = "0.0.1"
    author : str = "mthspm"
    
    host: str = "0.0.0.0"
    port: int = 10000

config = Config()
app = FastAPI()
app.description = " ".join([config.description, config.author, config.version])
app.title = config.title
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