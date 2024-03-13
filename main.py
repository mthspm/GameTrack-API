from typing import Union

from fastapi import FastAPI
from pydantic import BaseModel

from tibia import Tibia

import uvicorn

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/tibia/news")
def getTibiaNews():
    tibia = Tibia()
    return tibia.getNews()

@app.get("/tibia/lastnew")
def getTibiaLastNew():
    tibia = Tibia()
    return tibia.getLastNew()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)