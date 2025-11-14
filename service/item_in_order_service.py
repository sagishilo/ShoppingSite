
from typing import List
from model.item_in_order_response import ItemInOrderResponse
from repository import item_in_order_repository
from model.exceptions import CustomExceptions
ex = CustomExceptions()

## Checks if an item in order exists by its id
## Returns True if exists, False otherwise
async def validate_item_in_order_exists(item_in_order_id: int) -> bool:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    return item_in_order is not None


## Returns an item in order by its id
## Raises exception if not found
async def get_item_in_order_by_id(item_in_order_id: int) -> ItemInOrderResponse:
    item_in_order = await item_in_order_repository.get_by_id(item_in_order_id)
    if not item_in_order:
        raise ex.item_in_order_not_found_exception()
    return item_in_order


## Returns all items in a specific order
async def get_all_items_by_order_id(order_id: int) -> List[ItemInOrderResponse]:
    return await item_in_order_repository.get_all_by_order_id(order_id)


## Adds a new item to an order
## Returns the id of the newly created item_in_order record
async def add_item_to_order(order_id: int, item_id: int, amount_in_order: int) -> int:
    return await item_in_order_repository.add_item_to_order(order_id, item_id, amount_in_order)


## Updates the amount of an item in order
## Returns the number of rows updated
async def update_item_amount_in_order(item_in_order_id: int, new_amount_in_order: int) -> int:
    if not await validate_item_in_order_exists(item_in_order_id):
        raise ex.item_in_order_not_found_exception()
    return await item_in_order_repository.update_item_amount_in_order(item_in_order_id, new_amount_in_order)


## Deletes an item from an order by its id
## Returns the number of rows deleted
async def delete_item_in_order_by_id(item_in_order_id: int) -> int:
    if not await validate_item_in_order_exists(item_in_order_id):
        raise ex.item_in_order_not_found_exception()
    return await item_in_order_repository.delete_item_in_order_by_id(item_in_order_id)
