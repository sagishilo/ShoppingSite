from typing import List, Optional
from model.exceptions import CustomExceptions
from model.favorite_item_request import FavoriteItemRequest
from model.item_response import ItemResponse
from repository import favorite_item_repository
from service import user_service, item_service

ex=CustomExceptions()



## Receives a user id
## Checks if the user exists and retrieves the user's favorite items
## Returns the user's favorite items list

async def get_all_by_user_id(user_id: int) -> List[ItemResponse]:
    user= await user_service.get_by_id(user_id)
    if not user:
        raise ex.user_not_found_exception()
    fav_list = await favorite_item_repository.get_all_by_user_id(user_id)
    return fav_list



## Retrieves items popularity statistics
## Calls the repository to get favorites count per item
## Returns the popularity statistics list

async def get_items_popularity_stats():
    return await favorite_item_repository.get_items_popularity_stats()



## Receives a favorite item request
## Checks if the user and item exist and verifies the item is not already in favorites
## Adds the item to favorites and returns the new favorite id

async def add_item_to_fav(fav: FavoriteItemRequest) -> Optional[int]:
    user = await user_service.get_by_id(fav.user_id)
    if not user:
        raise ex.user_not_found_exception()
    item= await item_service.get_item_by_id(fav.item_id)
    if not item:
        raise ex.item_not_found_exception()
    if await favorite_item_repository.is_fav(fav):
        raise ex.item_fav_already_exception()
    return await favorite_item_repository.add_item_to_fav(fav)


## Receives an item id
## Checks if the item exists and removes it from all favorites
## Returns nothing

async def delete_item(item_id: int):
    item = await item_service.get_item_by_id(item_id)
    if not item:
        raise ex.item_not_found_exception()
    await favorite_item_repository.delete_item(item_id)


## Receives a favorite item request
## Checks if the item is currently in the user's favorites
## Removes the item from favorites and returns the result

async def unfav_item(fav: FavoriteItemRequest):
    is_fav= await favorite_item_repository.is_fav(fav)
    if is_fav:
        return await favorite_item_repository.unfav_item(fav)
    raise ex.item_not_fav_exception()


## Receives a user id
## Removes all favorite items for that user
## Returns nothing

async def unfav_items_for_user(user_id: int):
    await favorite_item_repository.unfav_items_for_user(user_id)

