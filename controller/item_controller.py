from typing import List
from fastapi import APIRouter, HTTPException
from model.item import Item
from model.item_request import ItemRequest
from repository import item_repository

router = APIRouter(prefix="/item", tags=["item"])


## Returns an item by id
## gets -> int
## returns -> Item
@router.get("/{id}", response_model=Item)
async def get_item(id: int):
    try:
        item = await item_repository.get_by_id(id)
        return item
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all items
## returns -> List[Item]
@router.get("/", response_model=List[Item])
async def get_items():
    try:
        return await item_repository.get_all()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Creates a new item
## gets -> JSON of Item
## returns -> int (item id)
@router.post("/", response_model=int)
async def create_item(item: ItemRequest):
    try:
        new_item_id = await item_repository.create_item(item)
        return new_item_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Updates an existing item
## gets -> JSON of Item
## returns -> str message
@router.put("/{id}", response_model=str)
async def update_item(id: int, updated_item: ItemRequest):
    try:
        await item_repository.update_item(id, updated_item)
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Deletes a specific item
## gets -> int (item id)
## returns -> int (deleted item id)
@router.delete("/{id}", response_model=int)
async def delete_item(item_id: int):
    try:
        deleted_id = await item_repository.delete_item(item_id)
        return deleted_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
