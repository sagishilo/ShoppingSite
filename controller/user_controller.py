from typing import List
from fastapi import HTTPException
from fastapi import APIRouter

from model.login_request import LoginRequest
from model.user_response import UserResponse
from model.user_request import UserRequest
from service import user_service


router = APIRouter(prefix="/user", tags=["user"])


## Logs in a user
## gets -> JSON of LoginRequest
## returns -> UserResponse
@router.post("/auth/login", response_model=UserResponse)
async def login_endpoint(request: LoginRequest):
    user = await user_service.user_login(request)
    if user:
        return user

    raise HTTPException(status_code=400, detail="Invalid credentials")


## Returns a user by id
## gets -> int
## returns -> UserResponse
@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    try:
        return await user_service.get_by_id(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


## Returns all users
## returns -> List of UserResponse
@router.get("/", response_model=List[UserResponse])
async def get_users():
    try:
        return await user_service.get_all()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Creates a new user
## gets -> JSON of UserRequest
## returns -> int (user id)
@router.post("/")
async def create_user(user: UserRequest):
    try:
        ##print("this is user " + str(user.model_dump()))
        return await user_service.create_user(user)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))



## Deletes a specific user and all their related data
## gets -> int (user_id)
## returns -> str message
@router.delete("/{user_id}", response_model=str)
async def delete_user(user_id: int):
    try:
        return await user_service.delete_user(user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




## Updates an existing user
## gets -> JSON of UserRequest and int (user_id)
## returns -> str message
@router.put("/{user_id}", response_model=str)
async def update_user(user_id: int, updated_user: UserRequest):
    try:
        await user_service.update_user(user_id, updated_user)
        return "Update succeeded"
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))




