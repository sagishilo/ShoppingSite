import json
from typing import Optional, List
from model.favorite_item_request import FavoriteItemRequest
from model.item_response import ItemResponse
from repository import cache_repository
from repository.database import database

TABLE_NAME = "favorites_items"

##
async def get_all_by_user_id(user_id: int) -> List[ItemResponse]:
    cache_key = f"fav_items_{user_id}"

    if cache_repository.is_key_exists(cache_key):
        fav_items_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return [ItemResponse(**item) for item in fav_items_dict]

    query = f"""
    SELECT 
        i.id AS item_id,
        i.item_name,
        i.price,
        i.amount_in_stock,
        i.image_url
    FROM item i
    JOIN {TABLE_NAME} f ON i.id = f.item_id
    WHERE f.user_id = :user_id
    """
    rows = await database.fetch_all(query, {"user_id": user_id})
    formatted_results = []
    for row in rows:
        item_obj = ItemResponse(
            id=row["item_id"],
            item_name=row["item_name"],
            price=float(row["price"]),
            amount_in_stock=(row["amount_in_stock"]),
            image_url=row["image_url"] or ""
        )
        formatted_results.append(item_obj)

    items_json = json.dumps([item.model_dump() for item in formatted_results])
    cache_repository.create_cache_entity(cache_key, items_json)

    return formatted_results


async def get_items_popularity_stats():
    query = f"""
    SELECT 
        i.id AS item_id,
        i.item_name,
        i.price,
        COUNT(f.item_id) AS favorites_count
    FROM item i
    LEFT JOIN {TABLE_NAME} f ON i.id = f.item_id
    GROUP BY i.id, i.item_name, i.price
    ORDER BY favorites_count DESC;
    """
    rows = await database.fetch_all(query)

    return [
        {
            "id": row["item_id"],
            "name": row["item_name"],
            "price": float(row["price"]),
            "favorites_count": row["favorites_count"]
        }
        for row in rows
    ]


async def add_item_to_fav(fav: FavoriteItemRequest) -> Optional[int]:
    cache_key = f"fav_items_{fav.user_id}"

    query = f"""
    INSERT INTO {TABLE_NAME} (user_id, item_id)
    VALUES (:user_id, :item_id);
    """
    values = {
        "user_id": fav.user_id,
        "item_id": fav.item_id
    }
    new_fav_id = await database.execute(query=query, values=values)
    cache_repository.remove_cache_entity(cache_key)
    return new_fav_id



##Deletes a specific item
async def delete_item(item_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE item_id= :item_id"
    values ={"item_id":item_id }
    await database.execute(query, values)
    cache_repository.remove_cache_entity("all_items")
    return item_id


##Removes a specific item from fav
async def unfav_item(fav: FavoriteItemRequest):
    cache_key = f"fav_items_{fav.user_id}"

    query = f"DELETE FROM {TABLE_NAME} WHERE user_id= :user_id AND item_id= :item_id"
    values ={"user_id":fav.user_id,
             "item_id":fav.item_id}
    await database.execute(query, values)
    cache_repository.remove_cache_entity(cache_key)
    return fav.id



async def unfav_items_for_user(user_id: int):
    cache_key = f"fav_items_{user_id}"

    query = f"DELETE FROM {TABLE_NAME} WHERE user_id= :user_id"
    values ={"user_id":user_id}
    await database.execute(query, values)
    cache_repository.remove_cache_entity(cache_key)



async def is_fav(fav: FavoriteItemRequest):
    query = f"SELECT * FROM {TABLE_NAME} WHERE user_id= :user_id AND item_id= :item_id"""
    values = {"user_id": fav.user_id,
              "item_id": fav.item_id}
    row = await database.fetch_one(query, values)
    if row:
        return True
    return False
