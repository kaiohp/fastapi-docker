from typing import List

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Food(BaseModel):
    name: str
    price: float
    available: bool
    ingredients: List[str] = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/food/")
async def prepare_food(food: Food, delivery: bool = False):
    return {
        "message": f"preparing {food.name} and will cost {food.price}",
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
