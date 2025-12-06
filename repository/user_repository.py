from typing import Optional
from model.user_request import UserRequest
from model.user_response import UserResponse
from repository.database import database

TABLE_NAME = "users"

## Returns a user by id
async def get_by_id(user_id: int) -> Optional[UserResponse]:
    query = f"""
        SELECT 
            id AS user_id,
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name
        FROM {TABLE_NAME}
        WHERE id = :user_id;
    """
    row = await database.fetch_one(query, values={"user_id": user_id})
    if row is None:
        return None
    return UserResponse(**dict(row))


## Returns all users
async def get_all():
    query = f"""
        SELECT 
            id AS user_id,
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name
        FROM {TABLE_NAME}
    """
    result = await database.fetch_all(query)
    return [UserResponse(**dict(row)) for row in result]


async def create_user(new_user: UserRequest, hashed_password: str) -> int:
    query = f"""
        INSERT INTO {TABLE_NAME} 
        (first_name, last_name, email, phone, address, user_name, hashed_password)
        VALUES (:first_name, :last_name, :email, :phone, :address, :user_name, :hashed_password)
    """
    user_dict = new_user.model_dump()
    user_dict.pop("password", None)
    user_dict.pop("id", None)
    values = {**user_dict, "hashed_password": hashed_password}

    await database.execute(query, values)
    row = await database.fetch_one("SELECT LAST_INSERT_ID() AS id")
    return row["id"]


## Updates an existing user
async def update_user(user_id: int, updated_user: UserRequest, hashed_password: str) -> int:
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
    user_dict = updated_user.model_dump()
    user_dict.pop("password", None)
    user_dict.pop("id", None)
    values = {**user_dict, "hashed_password": hashed_password, "user_id": user_id}

    async with database.transaction():
        return await database.execute(query, values)


## Deletes a specific user
async def delete_user(user_id: int):
    query = f"DELETE FROM {TABLE_NAME} WHERE id = :user_id"
    await database.execute(query, {"user_id": user_id})
    return user_id


## Returns a user by user_name
async def get_by_user_name(user_name: str) -> Optional[UserResponse]:
    query = f"""
        SELECT 
            first_name,
            last_name,
            email,
            phone,
            address,
            user_name
        FROM {TABLE_NAME}
        WHERE user_name = :user_name;
    """
    row = await database.fetch_one(query, values={"user_name": user_name})
    if row is None:
        return None
    return UserResponse(**dict(row))
