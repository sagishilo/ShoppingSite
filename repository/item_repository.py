from typing import Optional, List
from model.item_request import ItemRequest
from model.item_response import ItemResponse
from repository.database import database

TABLE_NAME = "item"

## Returns an item by id
async def get_by_id(item_id: int) ->Optional[ItemResponse]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :id;
    """
    result = await database.fetch_one(query, values={"id": item_id})
    if result:
        return ItemResponse(
            id=result["id"],
            item_name=result["item_name"],
            price=result["price"],
            image_url=result["image_url"])
    else:
        return None


## Returns an items by accurate name
async def get_by_name(item_name: str) -> Optional[ItemResponse]:
    query = f"SELECT * FROM {TABLE_NAME} WHERE item_name = :item_name"
    row = await database.fetch_one(query, values={"item_name": item_name})
    if row:
        return ItemResponse(**row)
    return None

## Returns an items by partial name
async def search_by_name(item_name: str) -> list[ItemResponse]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE item_name LIKE :item_name;
    """
    search_value = f"%{item_name}%"

    results = await database.fetch_all(query, values={"item_name": search_value})
    return [ItemResponse(**row) for row in results]


## Returns all items
async def get_all() ->List[ItemResponse]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    items = [ItemResponse(
        id=row["id"],
        item_name=row["item_name"],
        price=row["price"],
        image_url=row["image_url"]) for row in result]
    return items


## Creates a new item
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
    row = await database.fetch_one("SELECT LAST_INSERT_ID() AS id")
    return row["id"]



## Updates an existing item
async def update_item(id: int, updated_item: ItemRequest) -> int:
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
    return result


## Updates an existing item's amount
async def update_amount(id: int, updated_amount: int) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET
        amount_in_stock = :amount_in_stock
        WHERE id = :id
    """
    values = {
        "amount_in_stock":updated_amount,
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

