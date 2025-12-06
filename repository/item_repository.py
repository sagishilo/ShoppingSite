from typing import Optional, List

from model.item import Item
from model.item_request import ItemRequest
from repository.database import database

TABLE_NAME = "item"

## Returns an item by id
async def get_by_id(id: int) ->Optional[Item]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :id;
    """
    result = await database.fetch_one(query, values={"id": id})
    if result:
        return Item(**result)
    else:
        return None


## Returns an items by partial name
async def get_by_name(item_name: str) -> list[Item]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE item_name LIKE :item_name;
    """

    search_value = f"%{item_name}%"

    results = await database.fetch_all(query, values={"item_name": search_value})
    return [Item(**row) for row in results]


## Returns all items
async def get_all() ->List[Item]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    items = [Item(**dict(row)) for row in result]
    return items


## Creates a new item
async def create_item(new_item: ItemRequest) -> Optional[int]:
    query = f"""
    INSERT INTO {TABLE_NAME} (item_name, price, amount_in_stock)
    VALUES (:item_name, :price, :amount_in_stock)
    """
    values = {
        "item_name": new_item.item_name,
        "price": new_item.price,
        "amount_in_stock": new_item.amount_in_stock
    }
    await database.execute(query, values)
    row = await database.fetch_one("SELECT LAST_INSERT_ID() AS id")
    return row["id"]



## Updates an existing item
async def update_item(id: int, updated_item: ItemRequest) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET item_name = :item_name,
        price = :price,
        amount_in_stock = :amount_in_stock
    WHERE id = :id
    """
    values = {
        "item_name": updated_item.item_name,
        "price": updated_item.price,
        "amount_in_stock": updated_item.amount_in_stock,
        "id": id,
    }

    async with database.transaction():
        result = await database.execute(query, values)
    return result


##Deletes a specific item
async def delete_item(item_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id= :id"
    values ={"id":item_id }
    await database.execute(query, values)
    return item_id
