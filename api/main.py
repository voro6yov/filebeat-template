from typing import Optional
from pydantic import BaseModel, Field

from fastapi import FastAPI, Query, Path, Body, status, Depends
from fastapi.security import OAuth2PasswordBearer


class Item(BaseModel):
    name: str
    description: Optional[str] = Field(
        None, title="The description of the item", max_length=300
    )
    price: float = Field(
        ..., gt=0, description="The price must be greater than zero"
    )
    tax: Optional[float] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Foo",
                "description": "A very nice Item",
                "price": 35.4,
                "tax": 3.2,
            }
        }


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.get("/")
async def root():
    return {"message": "hello, world!"}


@app.get("/items/{item_id}")
async def read_item(
    token: str = Depends(oauth2_scheme),
    item_id: int = Path(..., title="The ID of the item to get", gt=1),
    q: Optional[str] = Query(None, alias="item-query"),
    short: bool = False,
):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item."})
    item.update({"token": token})
    return item


@app.post(
    "/items/", response_model=Item, status_code=status.HTTP_201_CREATED
)
async def create_item(item: Item = Body(..., embed=True)) -> Item:
    """
    Creates item.
    """
    item_dict = item.dict()
    if item.tax:
        price_with_tax = item.price + item.tax
        item_dict.update({"price_with_tax": price_with_tax})
    return item_dict


@app.get("/users/me")
async def read_user_me():
    return {"user": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: str):
    return {"user_id": user_id}


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int,
    item_id: str,
    q: Optional[str] = None,
    short: bool = False,
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update({"description": "This is an amazing item."})
    return item
