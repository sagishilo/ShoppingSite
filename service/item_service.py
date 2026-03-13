from typing import List, Optional

from model.exceptions import CustomExceptions
from model.item import Item
from model.item_request import ItemRequest
from model.item_response import ItemResponse
from repository import item_repository
from service import favorite_item_service

ex=CustomExceptions()



## Checks if item name is unique
## Returns True if unique, False if it exists

async def validate_unique_item_name(item_name: str) -> bool:
    existing_item = await item_repository.get_by_name(item_name)
    return existing_item is None



## Checks if an item with the given name exists
## Raises exception if not found
## Returns the item by name

async def get_items_by_name(item_name: str) -> ItemResponse:
    item_list= await item_repository.get_by_name(item_name)
    if not item_list:
        raise ex.item_not_found_exception()
    return item_list


## Checks if an item with the given id exists
## Raises exception if not found
## Returns the item by id

async def get_item_by_id(item_id: int) -> ItemResponse:
    item=  await item_repository.get_by_id(item_id)
    if not item:
        raise ex.item_not_found_exception()
    return item


## Gets full item details by id
## Raises exception if not found
## Returns full item

async def get_full_item(item_id: int) -> Item:
    item=  await item_repository.get_full_item(item_id)
    if not item:
        raise ex.item_not_found_exception()
    return item


## Checks if an item exists by id
## Raises exception if not found
## Returns stock amount

async def get_stock(item_id: int) -> Optional[int]:
    stock=  await item_repository.get_stock(item_id)
    if not stock:
        raise ex.item_not_found_exception()
    return stock


## Returns all items
## No checks performed
## Returns list of all items

async def get_all() -> List[ItemResponse]:
    items_list= await item_repository.get_all()
    return items_list


## Checks if the new item's name is unique
## Raises exception if name taken
## Creates the item and returns its id

async def create_item(new_item: ItemRequest):
    if await validate_unique_item_name(new_item.item_name):
        return await item_repository.create_item(new_item)
    else:
        raise ex.itemname_taken_exception()




## Checks if the item exists by id
## Checks if updated name is unique if changed
## Raises exceptions if not found or name taken
## Updates the item and returns result

async def update_item(item_id: int, updated_item: ItemRequest):
    existing_item = await item_repository.get_by_id(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    if updated_item.item_name != existing_item.item_name:
        is_unique = await validate_unique_item_name(updated_item.item_name)
        if not is_unique:
            raise ex.itemname_taken_exception()
    return await item_repository.update_item(item_id, updated_item)




## Checks if the item exists by id
## Checks if stock is enough for requested amount
## Raises exception if not enough
## Updates stock and returns result

async def update_amount(item_id: int, amount_bought: int):
    existing_item = await item_repository.get_full_item(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    if existing_item.amount_in_stock-amount_bought<0:
        raise ex.not_in_stock(existing_item.amount_in_stock)
    return await item_repository.update_amount(item_id,existing_item.amount_in_stock-amount_bought)




## Checks if the item exists by id
## Raises exception if not found
## Deletes the item and related favorites
## Returns confirmation message

async def delete_item(item_id: int) -> Optional[str]:
    existing_item = await item_repository.get_by_id(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    await item_repository.delete_item(item_id)
    await favorite_item_service.delete_item(item_id)
    return f"The item with id {item_id} was deleted"
