from fastapi import APIRouter, Depends, Header

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)

from src.extension.db import users, roles
from src.dto.user import (
    UserCreate,
    UserInDB,
    UserRoleUpdate,
    UserStatusUpdate,
    UserUpdate,
)
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
    # response_model=UserInDB
)
async def create_user(
    user: UserCreate,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.ADD.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):

    try:
        role = await roles.find_one_by_conditions({"name": "default"})
        if not role:
            return BadRequestError(msg="Invalid Role").send()

        role = roles.serialize(role)
        role_id = role["_id"]
        req_body = user.dict()

        insert_data = {
            "role_id": roles.to_object_id(role_id),
            "name": req_body["name"],
            "email": req_body["email"],
            "status": req_body["status"],
            "gender": req_body["gender"],
        }

        resp = await users.insert_one(insert_data)
        # print("resp:::", resp)
        # print("resp.inserted_id:::", resp.inserted_id)
        # data = UserInDB(id=str(resp.inserted_id), **user.dict())
        # print("data:::", users.serialize(data))
        return SuccessResponse(msg="OK").send(data=str(resp.inserted_id))

    except Exception as E:
        print("e::", E)
        return InternalServerError(msg="Internal Err").send()


@user_route.put(
    "/update/{id}",
    # response_model=UserInDB
)
async def update_user(
    id: str,
    user: UserUpdate,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.UPDATE.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):
    try:
        req_body = user.dict()
        print("req_body::::::", req_body)
        user = await users.find_by_id(id)
        if not user:
            return BadRequestError(msg="Invalid User").send()

        resp = await users.update_one({"_id": users.to_object_id(id)}, req_body)

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Role").send()

        # return SuccessResponse(msg="OK").send(data=UserInDB(id=id, **role.dict()))
        return SuccessResponse(msg="OK").send(data=True)
    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.patch("/status/{user_id}")
async def update_user_status(
    user_id: str,
    status: UserStatusUpdate,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):
    try:

        req_body = status.dict()
        user = await users.find_by_id(id=user_id)

        if not user:
            return BadRequestError(msg="Invalid User").send()

        resp = await users.update_one(
            filter={"_id": users.to_object_id(user_id)},
            update={"status": req_body["status"]},
        )

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Updated").send()

        return SuccessResponse(msg="OK").send(data=True)

    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.patch("/role/{user_id}")
async def update_user_role(
    user_id: str,
    role: UserRoleUpdate,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):
    try:

        req_body = role.dict()
        print("req_body::::::", req_body)
        user = await users.find_by_id(id=user_id)

        if not user:
            return BadRequestError(msg="Invalid User").send()

        resp = await users.update_one(
            filter={"_id": users.to_object_id(user_id)},
            update={"role_id": users.to_object_id((req_body["role_id"]))},
        )

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Updated").send()

        return SuccessResponse(msg="OK").send(data=True)

    except Exception as E:
        print("EEEE::::::", str(E))
        return InternalServerError(msg=str(E)).send()


@user_route.get("", response_model=list[UserInDB])
async def list_users(
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):

    try:

        # resp = await users.find_list(page=1, page_size=10)
        resp = await users.get_users_with_roles()
        print("respLLL", resp)
        data = []

        for doc in resp:
            print("doc::", doc)
            data.append(roles.serialize(doc))

        return SuccessResponse(msg="OK").send(data=data)
    except Exception as E:
        print("ERRR:", E)
        return InternalServerError(msg=str(E)).send()


@user_route.get("/detail/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):
    try:

        resp = await users.get_user_detail_with_role(user_id)
        if not resp:
            return NotFoundError(msg="User not found").send()
        return SuccessResponse(msg="OK").send(data=users.serialize(resp))
    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@user_route.delete("/remove/{user_id}")
async def delete_user(
    user_id: str,
    create_user=Depends(
        verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    ),
    x_token: str = Header(...),
):
    try:
        resp = await users.delete_by_id(user_id)

        if resp.deleted_count == 0:
            return BadRequestError(msg="User not found").send()
        return SuccessResponse(msg="OK").send(data=True)

    except Exception as E:
        print("EEEE::::::", str(E))
        return InternalServerError(msg=str(E)).send()
