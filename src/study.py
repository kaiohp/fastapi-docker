from enum import Enum
from time import sleep
from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

import src.core.app_log

app = FastAPI()


class AvaliableFood(str, Enum):
    pizza = "pizza"
    taco = "taco"
    hamburguer = "hamburguer"


class Food(BaseModel):
    name: AvaliableFood
    price: float
    available: bool
    ingredients: list[str] = []


@app.get("/")
async def root():
    sleep(2)
    return {"message": "Hello Docker!!!"}


@app.post("/food/")
async def prepare_food(food: Food, delivery: bool = False):
    return {
        "message": f"preparing {food.name.value} and will cost {food.price}",
        "delivery": delivery,
    }


@app.post("/orders/")
async def prepare_orders(orders: List[Food], delivery: bool = False):
    total_price = sum(order.price for order in orders)
    return {
        "message": f"preparing {len(orders)} orders",
        "total_cost": total_price,
        "delivery": delivery,
    }


@app.get("/users/me")
async def read_user_me():
    return {"user_id": "the current user"}


@app.get("/users/{user_id}")
async def read_user(user_id: int):
    return {"user_id": user_id}


@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}


fake_items_db = [
    {"item_name": "Foo"},
    {"item_name": "Bar"},
    {"item_name": "Baz"},
]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]


"""
@app.get("/items/{item_id}")
async def read_itemv2(item_id: str, q: str | None = None, short: bool = False):
    item = {"item_id": item_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item
"""


@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {
                "description": "This is an amazing item that has a long description"
            }
        )
    return item


@app.get("/items/v2/{item_id}")
async def read_user_item2(
    item_id: AvaliableFood,
    delivery: bool,
    skip: int = 0,
    limit: int | None = None,
):
    item = {
        "item_id": item_id,
        "delivery": delivery,
        "skip": skip,
        "limit": limit,
    }
    return item


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None


@app.put("/items/v3/{item_id}")
async def update_item(item_id: int, item: Item):
    item_dict = item.model_dump()
    if item.tax:
        price_with_tax = item.price * (1 + item.tax)
        item_dict.update({"price_with_tax": round(price_with_tax, 2)})
    return {"item_id": item_id, **item_dict}


from typing import Annotated

from fastapi import Path, Query


@app.get("/items/query/")
async def read_items(
    q: Annotated[
        str | None,
        Query(
            title="Access Code",
            description="Query code for validate the access",
            alias="code-access",
            min_length=11,
            max_length=11,
            pattern=r"^\d{3}-\d{3}-\d{3}$",
            deprecated=True,
        ),
    ] = None
):
    results = {"items": [{"item_id": "Foo"}, {"item_id": "Bar"}]}
    if q:
        results.update({"q": q})
    return results


@app.get("/items/numeric/validations/{item_id}")
async def read_path_and_validate(
    item_id: Annotated[int, Path(title="The ID of the item to get")],
    q: Annotated[str | None, Query(alias="item-query")] = None,
):
    results = {"item_id": item_id}
    if q:
        results.update({"q": q})
    return results


from typing import Literal

from pydantic import Field, HttpUrl


class ExtensionsImageEnum(str, Enum):
    JPEG = ".jpeg"
    JPG = ".jpg"
    PNG = ".png"


class Image(BaseModel):
    url: HttpUrl
    name: str
    ext: ExtensionsImageEnum


class Item(BaseModel):
    name: str
    description: str | None = None
    price: float
    tax: float | None = None
    tags: set[str] = set()
    image: list[Image] | None = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Foo",
                    "description": "The pretender",
                    "price": 11.97,
                    "tax": 5.2,
                    "tags": ["rock", "metal"],
                    "image": [
                        {
                            "url": "https://example.com/the-pretender",
                            "name": "The Pretender",
                            "ext": ".png",
                        }
                    ],
                }
            ]
        }
    }


@app.put("/items/{item_id}")
async def update_item_v2(item_id: int, item: Item):
    results = {"item_id": item_id, "item": item}
    return results


from datetime import datetime, time, timedelta
from uuid import UUID

from fastapi import Body


@app.put("/items/v6/{item_id}")
async def read_items(
    item_id: UUID,
    start_datetime: Annotated[datetime, Body()],
    end_datetime: Annotated[datetime, Body()],
    process_after: Annotated[timedelta, Body()],
    repeat_at: Annotated[time | None, Body()] = None,
):
    start_process = start_datetime + process_after
    duration = end_datetime - start_process
    return {
        "item_id": item_id,
        "start_datetime": start_datetime,
        "end_datetime": end_datetime,
        "process_after": process_after,
        "repeat_at": repeat_at,
        "start_process": start_process,
        "duration": duration,
    }


from fastapi import Cookie, Header


@app.get("/items/cookie/")
async def read_items_cookie(
    ads_id: Annotated[str | None, Cookie()] = None,
    user_agent: Annotated[str | None, Header()] = None,
    x_token: Annotated[list[str] | None, Header()] = None,
):
    return {
        "ads_id": ads_id,
        "User-Agent": user_agent,
        "X-Token values": x_token,
    }


@app.post("/items/return_type/")
async def create_item(item: Item) -> Item:
    return item


@app.get("/items/return_type/")
async def read_items_return_type() -> list[Item]:
    return [
        Item(name="Portal Gun", price=42.0),
        Item(name="Plumbus", price=32.0),
    ]


from typing import Any

from pydantic import EmailStr


class BaseUser(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIn(BaseUser):
    password: str


class UserOut(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


# Don't do this in production!
@app.post("/user/", response_model=BaseUser)
async def create_user(user: UserIn) -> BaseUser:
    user.email = "123"
    return user


from fastapi import Response
from fastapi.responses import JSONResponse, RedirectResponse


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(
            url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        )
    return JSONResponse(
        content={"message": "Here's your interdimensional portal."}
    )


my_fake_db_short_url = {
    "2QglpGx": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "219haom": "https://www.youtube.com/watch?v=djV11Xbc914",
}

from fastapi import HTTPException


@app.get("/ka.ly/{url_code}")
async def redirect_portal(
    url_code: Annotated[str, Path(min_length=7, max_length=7)]
) -> Response:
    url_response = my_fake_db_short_url.get(url_code)
    if url_response is None:
        raise HTTPException(status_code=404, detail="Page not found")
    return RedirectResponse(url=url_response)


class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str | None = None


class UserIN(UserBase):
    password: str


class UserOut(UserBase):
    pass


class UserInDB(UserBase):
    hashed_password: str


def fake_password_hasher(raw_password: str):
    return "supersecret" + raw_password


async def fake_save_user(user_in: UserIn):
    """with open("database.json", "+a") as db:
        db.write(user_in_db.model_dump_json())
    print("User saved! ..not really")"""
    hashed_password = fake_password_hasher(user_in.password)
    user_in_db = UserInDB(
        **user_in.model_dump(), hashed_password=hashed_password
    )

    time.sleep(2)
    return user_in_db


from fastapi import status


@app.post(
    "/user/creation/",
    status_code=status.HTTP_201_CREATED,
    response_model=UserOut,
)
async def create_user_1(user_in: UserIn):
    user_saved = await fake_save_user(user_in)
    return user_saved


class BaseItem(BaseModel):
    description: str
    type: str


class CarItem(BaseItem):
    type: str = "car"


class PlaneItem(BaseItem):
    type: str = "plane"
    size: int


items = {
    "item1": {
        "description": "All my friends drive a low rider",
        "type": "car",
    },
    "item2": {
        "description": "Music is my aeroplane, it's my aeroplane",
        "type": "plane",
        "size": 5,
    },
}

from typing import Union


@app.get("/items/baseitem/{item_id}", response_model=Union[PlaneItem, CarItem])
async def read_item(item_id: str):
    return items[item_id]


from fastapi import File, Form, UploadFile
from fastapi.responses import HTMLResponse


@app.post("/login/", status_code=status.HTTP_201_CREATED)
async def login(username: str = Form(), password: str = Form()):
    return {"username": username}


@app.post("/files/")
async def create_files(files: Annotated[list[bytes], File()]):
    return {"file_sizes": [len(file) for file in files]}


@app.post("/uploadfiles/")
async def create_upload_files(files: list[UploadFile]):
    return {"filenames": [file.filename for file in files]}


@app.get("/app/")
async def main():
    content = """
<body>
<form action="/files/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
<form action="/uploadfiles/" enctype="multipart/form-data" method="post">
<input name="files" type="file" multiple>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


from fastapi import HTTPException

items = {"foo": "The Foo Wrestlers"}


@app.get("/items-header/{item_id}")
async def read_item_header(item_id: str):
    if item_id not in items:
        raise HTTPException(
            status_code=404,
            detail="Item not found",
            headers={"X-Error": "There goes my error"},
        )
    return {"item": items[item_id]}


from fastapi import Request
from fastapi.responses import JSONResponse


class UnicornException(Exception):
    def __init__(self, name: str):
        self.name = name


@app.exception_handler(UnicornException)
async def unicorn_exception_handler(request: Request, exc: UnicornException):
    return JSONResponse(
        status_code=418,
        content={
            "message": f"Oops! {exc.name} did something. There goes a rainbow..."
        },
    )


@app.get("/unicorns/{name}")
async def read_unicorn(name: str):
    if name == "yolo":
        raise UnicornException(name=name)
    return {"unicorn_name": name}


from fastapi.encoders import jsonable_encoder


class Item(BaseModel):
    name: str | None = None
    description: str | None = None
    price: float | None = None
    tax: float = 10.5
    tags: list[str] = []


items = {
    "foo": {"name": "Foo", "price": 50.2},
    "bar": {
        "name": "Bar",
        "description": "The bartenders",
        "price": 62,
        "tax": 20.2,
    },
    "baz": {
        "name": "Baz",
        "description": None,
        "price": 50.2,
        "tax": 10.5,
        "tags": [],
    },
}


@app.get("/items/body/{item_id}", response_model=Item)
async def read_item(item_id: str):
    return items[item_id]


@app.put("/items/body/{item_id}", response_model=Item)
async def update_item(item_id: str, item: Item):
    update_item_encoded = jsonable_encoder(item)
    items[item_id] = update_item_encoded
    return update_item_encoded


@app.patch("/items/body/{item_id}", response_model=Item)
async def update_partial_item(item_id: str, item: Item):
    stored_item_data = items[item_id]
    stored_item_model = Item(**stored_item_data)
    update_data = item.model_dump(exclude_unset=True)
    updated_item = stored_item_model.model_copy(update=update_data)
    items[item_id] = jsonable_encoder(updated_item)
    return updated_item


from typing import Annotated

from fastapi import Depends


async def common_parameters(
    q: str | None = None, skip: int = 0, limit: int = 100
):
    return {"q": q, "skip": skip, "limit": limit}


CommonsParam = Annotated[dict, Depends(common_parameters)]


@app.get("/dependencies/items/")
async def read_items_dependencies(commons: CommonsParam):
    return commons


@app.get("/dependencies/users/")
async def read_users_dependencies(commons: CommonsParam):
    return commons


class CommonQueryParams:
    def __init__(self, q: str | None = None, skip: int = 0, limit=100):
        self.q = q
        self.skip = skip
        self.limit = limit

    def __repr__(self):
        return f"CommonQueryParams({self.q=}, {self.skip=}, {self.limit=})"


@app.get("dependecies/class/items/")
async def read_items(
    commos: Annotated[CommonQueryParams, Depends(CommonQueryParams)]
):
    response = {}
    if commos.q:
        response.update({"q": commos.q})


from typing import Annotated

from fastapi import Depends, Header, HTTPException


async def verify_token(x_token: Annotated[str, Header()]):
    if x_token != "fake-super-secret-token":
        raise HTTPException(status_code=400, detail="X-Token header invalid")


async def verify_key(x_key: Annotated[str, Header()]):
    if x_key != "fake-super-secret-key":
        raise HTTPException(status_code=400, detail="X-Key header invalid")
    return x_key


@app.get("/items/", dependencies=[Depends(verify_token), Depends(verify_key)])
async def read_items():
    return [{"item": "Foo"}, {"item": "Bar"}]


data = {
    "plumbus": {"description": "Freshly pickled plumbus", "owner": "Morty"},
    "portal-gun": {"description": "Gun to create portals", "owner": "Rick"},
}


class OwnerError(Exception):
    pass


def get_username():
    try:
        yield "Rick"
    except OwnerError as e:
        raise HTTPException(status_code=400, detail=f"Owner error: {e}")


@app.get("/dependencies/yield/items/{item_id}")
def get_item(item_id: str, username: Annotated[str, Depends(get_username)]):
    if item_id not in data:
        raise HTTPException(status_code=404, detail="Item not found")
    item = data[item_id]
    if item["owner"] != username:
        raise OwnerError(username)
    return item
