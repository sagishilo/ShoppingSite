from typing import List, Optional
from model.exceptions import CustomExceptions
from model.favorite_item_request import FavoriteItemRequest
from model.item_response import ItemResponse
from repository import favorite_item_repository
from service import user_service, item_service

ex=CustomExceptions()


async def get_all_by_user_id(user_id: int) -> List[ItemResponse]:
    user= await user_service.get_by_id(user_id)
    if not user:
        raise ex.user_not_found_exception()
    fav_list = await favorite_item_repository.get_all_by_user_id(user_id)
    return fav_list


async def get_items_popularity_stats():
    return await favorite_item_repository.get_items_popularity_stats()


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


async def delete_item(item_id: int):
    item = await item_service.get_item_by_id(item_id)
    if not item:
        raise ex.item_not_found_exception()
    await favorite_item_repository.delete_item(item_id)


async def unfav_item(fav: FavoriteItemRequest):
    is_fav= await favorite_item_repository.is_fav(fav)
    if is_fav:
        return await favorite_item_repository.unfav_item(fav)
    return ex.item_not_fav_exception()


