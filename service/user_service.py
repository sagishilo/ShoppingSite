from typing import Optional, List
from model.exceptions import CustomExceptions
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository import user_repository
from passlib.context import CryptContext

from service import order_service

ex=CustomExceptions()
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return bcrypt_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt_context.verify(plain_password, hashed_password)





##Checks if the wanted username exists
## If it does - Return user by username
async def get_user_by_user_name(user_name: str) -> UserResponse:
    user= await user_repository.get_by_user_name(user_name)
    if not user:
        raise ex.user_not_found_exception()
    return user


##Checks if the wanted username exists
## If it does - Return true
async def validate_unique_user_name(user_name: str) -> bool:
    existing_user = await user_repository.get_by_user_name(user_name)
    return existing_user is None



##Checks if the wanted user exists
## If it does - Return user by id
async def get_by_id(user_id: int) -> Optional[UserResponse]:
    user = await user_repository.get_by_id(user_id)
    if not user:
        raise ex.user_not_found_exception()
    return user




## Returns all users
async def get_all() -> List[UserResponse]:
    users_list= await user_repository.get_all()
    return users_list




## Checks if the wanted user exists
## If it doesn't - Creates a new user
async def create_user(new_user: UserRequest):
    if await validate_unique_user_name(new_user.user_name):
        hashed_password = get_password_hash(new_user.password)
        await user_repository.create_user(new_user, hashed_password)
    else:
        print("username is already existing")
        raise ex.username_taken_exception()


## Checks if the wanted user exists
## If it does - Checks if the given user id matches the updated user's id
## If ids match - Updates the user
async def update_user(user_id: int, updated_user: UserRequest):
    existing_user = await user_repository.get_by_id(user_id)
    if not existing_user:
        raise ex.user_not_found_exception()
    if updated_user.user_name != existing_user.user_name:
        is_unique = await validate_unique_user_name(updated_user.user_name)
        if not is_unique:
            raise ex.username_taken_exception()
    hashed_password = get_password_hash(updated_user.password)
    return await user_repository.update_user(user_id, updated_user, hashed_password)



## Checks if the wanted user exists
## Deletes the user and his temp order if exist
async def delete_user(user_id: int) -> Optional[str]:
    existing_user = await user_repository.get_by_id(user_id)
    if not existing_user:
        raise ex.user_not_found_exception()
    temp_order_id=await order_service.get_temp_order_id_by_user(user_id)
    if temp_order_id is not None:
        await order_service.delete_order(temp_order_id)
    await user_repository.delete_user(user_id)
    return f"The user with id {user_id} was deleted"

