from typing import List, Optional
from fastapi import APIRouter, HTTPException
from model.order import Order
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from repository import order_repository
from service import order_service

router = APIRouter(prefix="/order", tags=["order"])


## Returns an order by id
## gets -> int
## returns -> OrderResponse
@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int):
    try:
        order = await order_service.get_order_by_id(order_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all orders
## returns -> List[OrderResponse]
@router.get("/", response_model=List[OrderResponse])
async def get_orders():
    try:
        return await order_service.get_all()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all orders for user
## Gets a user ID -> int
## returns -> List[Order]
@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_orders_for_user(user_id: int):
    try:
        return await order_service.get_all_orders_by_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Creates a new order
## gets -> JSON of Order
## returns -> int (order id)
@router.post("/", response_model=int)
async def create_order(order: OrderRequest):
    try:
        new_order_id = await order_service.create_order(order)
        return new_order_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Updates an existing order
## gets -> JSON of Order
## returns -> str message
@router.put("/{order_id}", response_model=str)
async def update_order(order_id: int, updated_order: Order):
    try:
        await order_service.update_order(order_id, updated_order)
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Deletes a specific order
## gets -> int (order id)
## returns -> int (deleted order id)
@router.delete("/{order_id}", response_model=int)
async def delete_order(order_id: int):
    try:
        deleted_id = await order_service.delete_order(order_id)
        return deleted_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Returns a temp order by id
## gets -> int
## returns -> OrderResponse
@router.get("/user/temp/{buyer_id}", response_model=Optional[OrderResponse])
async def get_temp_order_by_buyer(buyer_id: int):
    try:
        order = await order_service.get_temp_order_by_user(buyer_id)
        return order
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))