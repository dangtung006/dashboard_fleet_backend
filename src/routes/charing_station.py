from fastapi import APIRouter
from src.dto.charing_station import CharingStationCreate, CharingStationInDB

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import charing_stations

charing_station_route = APIRouter(tags=["Charing Stations"])


@charing_station_route.post(
    "/add",
    # response_model=RoleInDB
)
async def create_charing_station(role: CharingStationCreate):
    try:
        resp = await charing_stations.insert_one(role.dict())
        if resp.inserted_id:
            createdRole = await charing_stations.find_by_id(
                charing_stations.to_object_id(str(resp.inserted_id))
            )
        return SuccessResponse(msg="OK").send(data=charing_stations.serialize(createdRole))
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.put("/update/{role_id}", response_model=CharingStationInDB)
async def update_charing_station(role_id: str, role: CharingStationCreate):
    try:
        req_body = role.dict()
        data = await charing_stations.find_by_id(id=role_id)

        if not data:
            return BadRequestError(msg="Role Not Found").send()

        resp = await charing_stations.update_one({"_id": charing_stations.to_object_id(role_id)}, req_body)
        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid request").send()

        # return SuccessResponse(msg="OK").send(data=RoleInDB(id=role_id, **role.dict()))
        return SuccessResponse(msg="OK").send(data={**req_body, "_id": role_id})
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.get("", response_model=list[CharingStationInDB])
async def list_charing_stations():
    # roles = await db.roles.find().to_list(100)
    # return [RoleInDB(id=str(r["_id"]), **r) for r in roles]
    try:
        resp = await charing_stations.find_list(page=1, page_size=10)
        roleList = []

        async for doc in resp:
            roleList.append(charing_stations.serialize(doc))

        return SuccessResponse(msg="OK").send(data=roleList)
    except Exception as E:
        return InternalServerError(msg=str(E))



@charing_station_route.get("/{role_id}", response_model=CharingStationInDB)
async def get_charing_station(role_id: str):
    try:
        resp = await charing_stations.find_by_id(id=role_id)
        if not resp:
            return NotFoundError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=resp)
    except Exception as E:
        return InternalServerError(msg=str(E))


@charing_station_route.delete("/delete/{role_id}")
async def delete_charing_station(role_id: str):
    try:
        resp = await charing_stations.delete_by_id(role_id)
        if resp.deleted_count == 0:
            return BadRequestError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=True)
    except Exception as E:
        return InternalServerError(msg=str(E))
