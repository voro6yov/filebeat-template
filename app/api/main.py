import sys
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from loguru import logger

logger.add(
    "./logs/file.log",
    format="app-logs - {level} - {message}",
    rotation="500 MB"
)

app = FastAPI()


db = {}


class Item(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    tax: Optional[float] = None


@app.get("/items/{item_name}")
async def read_item(item_name: str):
    logger.info(f"[Reading an item] - {item_name}")
    item = db.get(item_name)
    if not item:
        logger.error(f"[Item not found] - {item_name}")
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@app.post("/items/")
async def create_item(item: Item):
    logger.info(f"[Creating an item] - {item.name}")
    if item.name in db:
        logger.error(f"[Item already exist] - {item.name}")
        raise HTTPException(
            status_code=403, detail="Item already exist"
        )
    item_dict = item.dict()
    if item.tax:
        logger.info(f"[Calculating price with tax] - tax: {item.tax}")
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    db[item.name] = item
    return item_dict
