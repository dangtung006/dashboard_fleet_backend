from fastapi import APIRouter
from src.dto.role import RoleInDB, RoleCreate, PermisionUpdate

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import roles

role_route = APIRouter(tags=["Roles"])


@role_route.post(
    "/add",
    # response_model=RoleInDB
)
async def create_role(role: RoleCreate):
    try:
        resp = await roles.insert_one(role.dict())
        if resp.inserted_id:
            createdRole = await roles.find_by_id(
                roles.to_object_id(str(resp.inserted_id))
            )
        return SuccessResponse(msg="OK").send(data=roles.serialize(createdRole))
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.put("/update/{role_id}", response_model=RoleInDB)
async def update_role(role_id: str, role: RoleCreate):
    try:
        req_body = role.dict()
        data = await roles.find_by_id(id=role_id)

        if not data:
            return BadRequestError(msg="Role Not Found").send()

        resp = await roles.update_one({"_id": roles.to_object_id(role_id)}, req_body)
        # print("resp:::", resp.acknowledged)
        # print("resp:::", resp.matched_count)
        # print("resp:::", resp.modified_count)
        # print("resp:::", resp.raw_result)

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid request").send()

        # return SuccessResponse(msg="OK").send(data=RoleInDB(id=role_id, **role.dict()))
        return SuccessResponse(msg="OK").send(data={**req_body, "_id": role_id})
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.patch("/permision/{role_id}")
async def update_role_permission(
    role_id: str,
    permision: PermisionUpdate,
    # create_user=Depends(
    #     verify_permission(USER_AUTH_TYPE.VIEW.value, USER_AUTH_RESOURCE.USER.value)
    # ),
    # x_token: str = Header(...),
):
    try:

        req_body = permision.dict()
        resource = req_body["resource"]
        action = req_body["action"]
        val = req_body["val"]

        if not resource or not action:
            return BadRequestError(msg="Invalid request").send()

        role = await roles.find_by_id(id=role_id)

        if not role:
            return BadRequestError(msg="Invalid User").send()

        permisionUpdate = f"permissions.{resource}.{action}"
        resp = await roles.update_one(
            filter={"_id": roles.to_object_id(role_id)},
            update={permisionUpdate: val},
        )

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Updated").send()

        return SuccessResponse(msg="OK").send(data=True)

    except Exception as E:
        return InternalServerError(msg=str(E)).send()


@role_route.get("", response_model=list[RoleInDB])
async def list_roles():
    # roles = await db.roles.find().to_list(100)
    # return [RoleInDB(id=str(r["_id"]), **r) for r in roles]
    try:
        resp = await roles.find_list(page=1, page_size=10)
        roleList = []

        async for doc in resp:
            roleList.append(roles.serialize(doc))

        return SuccessResponse(msg="OK").send(data=roleList)
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.get("/permissions")
async def get_permissions():
    try:
        configs = {
            "add": {
                "monitor": False,
                "robot": False,
                "robot_detail": False,
                "caller": False,
                "charging_station": False,
                "user": False,
                "user_detail": False,
                "statistics": False,
            },
            "view": {
                "monitor": False,
                "robot": False,
                "robot_detail": False,
                "caller": False,
                "charging_station": False,
                "user": False,
                "user_detail": False,
                "statistics": False,
            },
            "edit": {
                "monitor": False,
                "robot": False,
                "robot_detail": False,
                "caller": False,
                "charging_station": False,
                "user": False,
                "user_detail": False,
                "statistics": False,
            },
            "delete": {
                "monitor": False,
                "robot": False,
                "robot_detail": False,
                "caller": False,
                "charging_station": False,
                "user": False,
                "user_detail": False,
                "statistics": False,
            },
        }

        return SuccessResponse(msg="OK").send(data=configs)
    except Exception as E:
        print(str(E))
        return InternalServerError(msg=str(E))


@role_route.get("/{role_id}", response_model=RoleInDB)
async def get_role(role_id: str):
    try:
        resp = await roles.find_by_id(id=role_id)
        if not resp:
            return NotFoundError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.delete("/delete/{role_id}")
async def delete_role(role_id: str):
    try:
        resp = await roles.delete_by_id(role_id)
        if resp.deleted_count == 0:
            return BadRequestError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=True)
    except Exception as E:
        return InternalServerError(msg=str(E))
