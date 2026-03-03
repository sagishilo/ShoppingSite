from typing import List, Optional
from fastapi import APIRouter, HTTPException
from model.item import Item
from model.item_request import ItemRequest
from model.item_response import ItemResponse
from service import item_service

router = APIRouter(prefix="/item", tags=["item"])


## Returns an item by id
## gets -> int
## returns -> ItemResponse
@router.get("/{id}", response_model=ItemResponse)
async def get_item_by_id(id: int):
    try:
        item = await item_service.get_item_by_id(id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns an item by name
## gets -> str
## returns -> ItemResponse
@router.get("/item_name/{item_name}", response_model=List[ItemResponse])
async def get_item_by_name(item_name: str):
    try:
        items = await item_service.get_items_by_name(item_name)
        return items
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




## Returns all items
## returns -> List[ItemResponse]
@router.get("/", response_model=List[ItemResponse])
async def get_items():
    try:
        return await item_service.get_all()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Creates a new item
## gets -> JSON of Item
## returns -> int (item id)
@router.post("/", response_model=Optional[int])
async def create_item(item: ItemRequest):
    try:
        new_item_id = await item_service.create_item(item)
        return new_item_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Updates an existing item
## gets -> JSON of Item
## returns -> str message
@router.put("/{id}", response_model=str)
async def update_item(id: int, updated_item: ItemRequest):
    try:
        await item_service.update_item(id, updated_item)
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Deletes a specific item
## gets -> int (item id)
## returns -> int (deleted item id)
@router.delete("/{id}", response_model=str)
async def delete_item(id: int):
    try:
        deleted_id = await item_service.delete_item(id)
        return deleted_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
