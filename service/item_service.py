from typing import List, Optional

from model.exceptions import CustomExceptions
from model.item import Item
from model.item_request import ItemRequest
from repository import item_repository
ex=CustomExceptions()



##Checks if the wanted item name exists
## If it does - Return true
async def validate_unique_item_name(item_name: str) -> bool:
    existing_item = await item_repository.get_by_name(item_name)
    return existing_item is None



##Checks if the wanted item name exists
## If it does - Return item by name
async def get_items_by_name(item_name: str) -> List[Item]:
    item_list= await item_repository.get_by_name(item_name)
    if not item_list:
        raise ex.item_not_found_exception()
    return item_list


##Checks if the wanted item id exists
## If it does - Return item by id
async def get_item_by_id(item_id: int) -> Item:
    item=  await item_repository.get_by_id(item_id)
    if not item:
        raise ex.item_not_found_exception()
    return item



## Returns all items
async def get_all() -> List[Item]:
    items_list= await item_repository.get_all()
    return items_list



async def create_item(new_item: ItemRequest):
    if await validate_unique_item_name(new_item.item_name):
        return await item_repository.create_item(new_item)
    else:
        raise ex.itemname_taken_exception()




## Checks if the wanted item exists
## If it does - Checks if the given item id matches the updated item's id
## If ids match - Updates the item
async def update_item(item_id: int, updated_item: ItemRequest):
    existing_item = await item_repository.get_by_id(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    if updated_item.item_name != existing_item.item_name:
        is_unique = await validate_unique_item_name(updated_item.item_name)
        if not is_unique:
            raise ex.itemname_taken_exception()
    return await item_repository.update_item(item_id, updated_item)



async def update_amount(item_id: int, amount_bought: int):
    existing_item = await item_repository.get_by_id(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    if existing_item.amount_in_stock-amount_bought<0:
        raise ex.not_in_stock(existing_item.amount_in_stock)
    return await item_repository.update_amount(item_id,existing_item.amount_in_stock-amount_bought)




## Checks if the wanted item exists
## Deletes the item
async def delete_item(item_id: int) -> Optional[str]:
    existing_item = await item_repository.get_by_id(item_id)
    if not existing_item:
        raise ex.item_not_found_exception()
    await item_repository.delete_item(item_id)
    return f"The item with id {item_id} was deleted"


async def add_col():
    await item_repository.add_col()
