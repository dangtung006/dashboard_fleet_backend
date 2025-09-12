from fastapi import APIRouter, Depends

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)

from src.extension.db import users, roles
from src.dto.user import UserCreate, UserInDB
from src.dependencies.auth_gaurd import verify_permission
from src.app.app_conf import USER_AUTH_RESOURCE, USER_AUTH_TYPE

# from src.dependencies.permission import require_permission

# from bson import ObjectId

user_route = APIRouter(tags=["Users"])


# @user_route.get("/", response_model=list[UserInDB])
# async def list_users(current_user=Depends(require_permission("view", "user"))):
#     # users = await db.users.find().to_list(100)
#     # return [UserInDB(id=str(u["_id"]), **u) for u in users]
#     pass


@user_route.post(
    "/add",
    response_model=UserInDB,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.ADD.value, USER_AUTH_RESOURCE.USER.value)
    ),
)
async def create_user(user: UserCreate):

    try:
        role = await roles.find_by_id(id=user.role_id)
        if not role:
            return BadRequestError(msg="Invalid Role")
        resp = users.insert_one(*user.dict())
        return SuccessResponse(msg="OK").send(data=resp)

    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.put(
    "/update/{id}",
    response_model=UserInDB,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.EDIT.value, USER_AUTH_RESOURCE.USER.value)
    ),
)
async def create_user(id: str, user: UserCreate):
    try:
        role = await roles.find_by_id(id=user.role_id)
        if not role:
            return BadRequestError(msg="Invalid Role")

        resp = users.update_one({"_id": users.to_object_id(id)}, users.dict())

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Role").send()

        return SuccessResponse(msg="OK").send(data=UserInDB(id=id, **role.dict()))
    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.get(
    "/",
    response_model=list[UserInDB],
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW, USER_AUTH_RESOURCE.USER.value)
    ),
)
async def list_users():
    # users = await db.users.find().to_list(100)
    # return [UserInDB(id=str(u["_id"]), **u) for u in users]
    try:

        resp = await users.find_list(page=1, page_size=10)
        users = []

        async for doc in resp:
            users.append(roles.serialize(doc))

        return SuccessResponse(msg="OK").send(data=users)
    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.get(
    "/detail/{user_id}",
    response_model=UserInDB,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW, USER_AUTH_RESOURCE.USER.value)
    ),
)
async def get_user(user_id: str):
    try:

        resp = await users.find_by_id(id=user_id)
        if not resp:
            return NotFoundError(msg="User not found").send()
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.delete(
    "/remove/{user_id}",
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW, USER_AUTH_RESOURCE.USER.value)
    ),
)
async def delete_user(user_id: str):
    try:
        resp = await roles.delete_by_id(user_id)

        if resp.deleted_count == 0:
            return BadRequestError(msg="User not found").send()
        return SuccessResponse(msg="OK").send(data=resp)

    except Exception as E:
        return InternalServerError(msg=str(E)).send()
