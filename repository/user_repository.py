from typing import Optional, List
from model.user import User
from model.user_request import UserRequest
from repository.database import database

TABLE_NAME = "users"

## Returns a user by id
async def get_by_id(user_id: int) ->Optional[User]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    WHERE id = :user_id;
    """
    result = await database.fetch_one(query, values={"user_id": user_id})
    if result:
        return User(**result)
    else:
        return None


## Returns all users
async def get_all() ->List[User]:
    query = f"""
    SELECT *
    FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    return result


## Creates a new user
async def create_user(new_user: UserRequest, hashed_password: str)-> int:
    query= f"""
    INSERT INTO {TABLE_NAME} (first_name,last_name, email, phone, address, user_name, hashed_password )
    VALUES(:first_name, :last_name, :email, :phone, :address, :user_name, :hashed_password)
    """
    user_dict= new_user.model_dump()
    del user_dict["password"]
    del user_dict["id"]
    values = {**user_dict, "hashed_password": hashed_password}
    last_record_id = await database.execute(query, values)
    return last_record_id


## Updates an existing user
async def update_user(user_id: int, updated_user: UserRequest,  hashed_password: str) -> int:
    query = f"""
    UPDATE {TABLE_NAME}
    SET first_name = :first_name,
        last_name = :last_name,
        email = :email,
        phone = :phone,
        address = :address,
        user_name = :user_name,
        hashed_password = :hashed_password
    WHERE id = :user_id
    """
    user_dict = dict(updated_user)
    del user_dict["password"]
    values = {**user_dict, "hashed_password": hashed_password, "user_id": user_id}
    async with database.transaction():
        result = await database.execute(query, values)
    return result


##Deletes a specific user
async def delete_user(user_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id= :user_id"
    values ={"user_id":user_id }
    await database.execute(query, values)
    return user_id

