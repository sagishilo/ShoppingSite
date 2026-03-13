import json
from typing import Optional, List
from model.item import Item
from model.item_request import ItemRequest
from model.item_response import ItemResponse
from repository import cache_repository
from repository.database import database
all_cache_key = "all_items"
TABLE_NAME = "item"



##Returns a specific item by its id
async def get_by_id(item_id: int) ->Optional[ItemResponse]:
    cache_key=f"item_{item_id}"
    if cache_repository.is_key_exists(cache_key):
        item_dict = json.loads(cache_repository.get_cache_entity(cache_key))
        return ItemResponse(**item_dict)

    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :id;
    """
    result = await database.fetch_one(query, values={"id": item_id})
    if result:
        item= ItemResponse(
            id=result["id"],
            item_name=result["item_name"],
            price=result["price"],
            amount_in_stock=result["amount_in_stock"],
            image_url=result["image_url"])

        item_json = json.dumps(item.model_dump())
        cache_repository.create_cache_entity(cache_key, item_json)
        return item
    else:
        return None



##Returns the full item object by its id
async def get_full_item(item_id: int) ->Optional[Item]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :id;
    """
    result = await database.fetch_one(query, values={"id": item_id})
    if result:
        return Item(**result)
    else:
        return None



##Returns the stock amount for a specific item
async def get_stock(item_id: int) ->Optional[int]:
    query = f"""
    SELECT amount_in_stock
    FROM {TABLE_NAME}
    WHERE id = :id;
    """
    result = await database.fetch_one(query, values={"id": item_id})
    if result:
        return result["amount_in_stock"]
    else:
        return None


##Returns an item by its exact name
async def get_by_name(item_name: str) -> Optional[ItemResponse]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE item_name = :item_name"
    row = await database.fetch_one(query, values={"item_name": item_name})
    if row:
        return ItemResponse(**row)
    return None



##Returns items by partial name match
async def search_by_name(item_name: str) -> list[ItemResponse]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE item_name LIKE :item_name;
    """
    search_value = f"%{item_name}%"

    results = await database.fetch_all(query, values={"item_name": search_value})
    return [ItemResponse(**row) for row in results]




##Returns all items
async def get_all() ->List[ItemResponse]:
    if cache_repository.is_key_exists(all_cache_key):
        items_dict = json.loads(cache_repository.get_cache_entity(all_cache_key))
        return [ItemResponse(**item) for item in items_dict]

    else:
        query = f"""
        SELECT *
        FROM {TABLE_NAME}
        """
        result = await database.fetch_all(query)
        items = [ItemResponse(
            id=row["id"],
            item_name=row["item_name"],
            price=row["price"],
            amount_in_stock= row["amount_in_stock"],
            image_url=row["image_url"]) for row in result]

        items_json = json.dumps([item.model_dump() for item in items])
        cache_repository.create_cache_entity(all_cache_key, items_json)
        return items




##Creates a new item
async def create_item(new_item: ItemRequest) -> Optional[int]:
    query = f"""
    INSERT INTO {TABLE_NAME} (item_name, price, amount_in_stock,image_url)
    VALUES (:item_name, :price, :amount_in_stock, :image_url)
    """
    values = {
        "item_name": new_item.item_name,
        "price": new_item.price,
        "amount_in_stock": new_item.amount_in_stock,
        "image_url": new_item.image_url
    }
    await database.execute(query, values)
    cache_repository.remove_cache_entity(all_cache_key)
    row = await database.fetch_one("SELECT LAST_INSERT_ID() AS id")
    return row["id"]



##Updates a specific item by its id
async def update_item(id: int, updated_item: ItemRequest) -> int:
    cache_key=f"item_{id}"

    query = f"""
    UPDATE {TABLE_NAME}
    SET item_name = :item_name,
        price = :price,
        amount_in_stock = :amount_in_stock,
        image_url= :image_url
    WHERE id = :id
    """
    values = {
        "item_name": updated_item.item_name,
        "price": updated_item.price,
        "amount_in_stock": updated_item.amount_in_stock,
        "image_url": updated_item.image_url,
        "id": id,
    }

    async with database.transaction():
        result = await database.execute(query, values)
        cache_repository.remove_cache_entity(all_cache_key)
        cache_repository.remove_cache_entity(cache_key)

    return result




##Updates the stock amount of a specific item
async def update_amount(id: int, updated_amount: int) -> int:
    cache_key=f"item_{id}"

    query = f"""
    UPDATE {TABLE_NAME}
    SET
        amount_in_stock = :amount_in_stock
        WHERE id = :id
    """
    values = {
        "amount_in_stock":updated_amount,
        "id": id
    }
    async with database.transaction():
        result = await database.execute(query, values)
        cache_repository.remove_cache_entity(cache_key)
        cache_repository.remove_cache_entity(cache_key)

    return result




##Deletes a specific item by its id
async def delete_item(item_id: int):
    cache_key=f"item_{item_id}"

    query = f"DELETE FROM {TABLE_NAME} WHERE id= :id"
    values ={"id":item_id }
    await database.execute(query, values)
    cache_repository.remove_cache_entity(all_cache_key)
    cache_repository.remove_cache_entity(cache_key)

    return item_id

