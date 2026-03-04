from typing import List, Optional
from fastapi import APIRouter, HTTPException
from model.favorite_item_request import FavoriteItemRequest
from model.item_response import ItemResponse
from service import favorite_item_service

router = APIRouter(prefix="/fav-item", tags=["fav_item"])


## Returns items popularity stats
## returns -> list
@router.get("/pop/stats")
async def get_items_popularity_stats():
    try:
        items = await favorite_item_service.get_items_popularity_stats()
        return items
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns fav item by user
## gets -> int
## returns -> List of ItemResponse
@router.get("/{user_id}", response_model=List[ItemResponse])
async def get_all_by_user_id(user_id: int):
    try:
        items = await favorite_item_service.get_all_by_user_id(user_id)
        return items
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## makes an item a fav
## gets -> JSON of fav
## returns -> int (fav id)
@router.post("/", response_model=Optional[int])
async def add_item_to_fav(fav: FavoriteItemRequest):
    try:
        new_fav = await favorite_item_service.add_item_to_fav(fav)
        return new_fav
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Deletes a specific item from fav
## gets -> JSON of fav
## returns -> int (deleted fav id)
@router.delete("/remove/fav", response_model=Optional[int])
async def unfav_item(fav: FavoriteItemRequest):
    try:
        deleted_id = await favorite_item_service.unfav_item(fav)
        return deleted_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
