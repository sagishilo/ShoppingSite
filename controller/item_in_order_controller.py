from fastapi import APIRouter, HTTPException

from model.item_in_order import ItemInOrder
from model.item_in_order_response import ItemInOrderResponse
from service import item_in_order_service

router = APIRouter(prefix="/item-in-order", tags=["item_in_order"])


## Returns item_in_order by id
## gets -> int
## returns -> dict
@router.get("/{item_in_order_id}", response_model=ItemInOrderResponse)
async def get_item_in_order(item_in_order_id: int):
    try:
        result = await item_in_order_service.get_item_in_order_by_id(item_in_order_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Item in order not found")
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all items in a specific order
## gets -> order_id
## returns -> List[dict]
@router.get("/order/{order_id}")
async def get_items_by_order_id(order_id: int):
    try:
        results = await item_in_order_service.get_all_items_by_order_id(order_id)
        return results
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Adds a new item to an order
## gets -> order_id, id, amount_in_order
## returns -> int (new item_in_order id)
@router.post("/")
async def add_item_to_order(item: ItemInOrder):
    try:
        new_id = await item_in_order_service.add_item_to_order(item)
        return new_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Updates the amount of a specific item in an order
## gets -> item_in_order_id, new_amount_in_order
## returns -> str message
@router.put("/{item_in_order_id}")
async def update_item_amount(item_in_order_id: int, new_amount_in_order: int):
    try:
        result = await item_in_order_service.update_item_amount_in_order(item_in_order_id, new_amount_in_order)
        if not result:
            raise HTTPException(status_code=404, detail="Item in order not found")
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Deletes an item from an order by id
## gets -> item_in_order_id
## returns -> str message
@router.delete("/{item_in_order_id}")
async def delete_item_in_order(item_in_order_id: int):
    try:
        result = await item_in_order_service.delete_item_in_order_by_id(item_in_order_id)
        if not result:
            raise HTTPException(status_code=404, detail="Item in order not found")
        return "Delete succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
