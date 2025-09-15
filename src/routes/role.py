from fastapi import APIRouter
from src.dto.role import RoleInDB, RoleCreate

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import roles

role_route = APIRouter(tags=["Roles"])


@role_route.post("/add", response_model=RoleInDB)
async def create_role(role: RoleCreate):
    try:
        resp = roles.insert_one(role.dict())
        return SuccessResponse(msg="OK").send(
            data=RoleInDB(id=str(resp.inserted_id), **role.dict())
        )
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.put("/update/{role_id}", response_model=RoleInDB)
async def update_role(role_id: str, role: RoleCreate):
    try:
        resp = roles.update_one({"_id": roles.to_object_id(role_id)}, role.dict())

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid Role")

        return SuccessResponse(msg="OK").send(data=RoleInDB(id=role_id, **role.dict()))
    except Exception as E:
        return InternalServerError(msg=str(E))


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


@role_route.get("/{role_id}", response_model=RoleInDB)
async def get_role(role_id: str):
    try:
        resp = await roles.find_by_id(id=role_id)
        if not resp:
            return NotFoundError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@role_route.delete("/{role_id}")
async def delete_role(role_id: str):
    try:
        resp = await roles.delete_by_id(role_id)
        if resp.deleted_count == 0:
            return BadRequestError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


# # Permission
# @role_route.update_permission("/{role_id}")
# async def delete_role(role_id: str):
#     try:
#         # resp = await roles.delete_by_id(role_id)
#         # if resp.deleted_count == 0:
#         #     return BadRequestError(msg="Role not found")
#         # return SuccessResponse(msg="OK").send(data=resp)
#         pass
#     except Exception as E:
#         return InternalServerError(msg=str(E))
