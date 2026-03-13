from typing import List, Optional
from fastapi import APIRouter, HTTPException
from model.order_request import OrderRequest
from model.order_response import OrderResponse
from model.order_summary import OrderSummary
from service import order_service

router = APIRouter(prefix="/order", tags=["order"])

## Returns closed orders summary for a specific user
## gets -> int (buyer_id)
## returns -> List of OrderSummary
@router.get("/user/closed/{buyer_id}", response_model=List[OrderSummary])
async def get_closed_orders_summary_by_user(buyer_id: int):
    try:
        closed_orders = await order_service.get_closed_orders_summary_by_user(buyer_id)
        return closed_orders
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
## returns -> List of OrderResponse
@router.get("/", response_model=List[OrderResponse])
async def get_orders():
    try:
        return await order_service.get_all()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all orders for a specific user
## gets -> int (user_id)
## returns -> List of OrderResponse
@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_orders_for_user(user_id: int):
    try:
        return await order_service.get_all_orders_by_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Creates a new order
## gets -> JSON of OrderRequest
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
async def update_order(order_id: int, updated_order: OrderRequest):
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



## Closes a specific order by id
## gets -> int (order_id)
## returns -> bool
@router.put("/close/{order_id}", response_model=bool)
async def close_order(order_id: int):
    try:
        await order_service.close_order(order_id)
        return True
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))