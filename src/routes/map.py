from fastapi import APIRouter
from src.dto.map import MapCreate, MapInDB

from src.helper.response import (
    BadRequestError,
    NotFoundError,
    SuccessResponse,
    InternalServerError,
)
from src.extension.db import robot_maps

robot_maps_route = APIRouter(tags=["Maps"])


@robot_maps_route.post(
    "/add",
    # response_model=RoleInDB
)
async def create_map(map: MapCreate):
    try:
        resp = await robot_maps.insert_one(map.dict())

        if resp.inserted_id:
            createdRole = await robot_maps.find_by_id(
                robot_maps.to_object_id(str(resp.inserted_id))
            )
        return SuccessResponse(msg="OK").send(data=robot_maps.serialize(createdRole))
    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.put(
    "/update/{map_id}", 
    # response_model=MapInDB
)
async def update_map(map_id: str, robotMap: MapCreate):
    try:
        req_body = robotMap.dict()
        data = await robot_maps.find_by_id(id=map_id)

        if not data:
            return BadRequestError(msg="Map Not Found").send()

        resp = await robot_maps.update_one(
            {"_id": robot_maps.to_object_id(map_id)}, req_body
        )

        if resp.modified_count == 0:
            return BadRequestError(msg="Invalid request").send()

        return SuccessResponse(msg="OK").send(data={**req_body, "_id": map_id})

    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.get("", response_model=list[MapInDB])
async def list_maps():
    try:
        resp = await robot_maps.find_list(page=1, page_size=10)
        roleList = []

        async for doc in resp:
            roleList.append(robot_maps.serialize(doc))

        return SuccessResponse(msg="OK").send(data=roleList)

    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.get("/{map_id}", response_model=MapInDB)
async def get_map(map_id: str):
    try:
        resp = await robot_maps.find_by_id(id=map_id)
        if not resp:
            return NotFoundError(msg="Role not found")
        return SuccessResponse(msg="OK").send(data=robot_maps.serialize(resp))

    except Exception as E:
        return InternalServerError(msg=str(E))


@robot_maps_route.delete("/delete/{map_id}")
async def delete_map(map_id: str):
    try:
        resp = await robot_maps.delete_by_id(map_id)
        if resp.deleted_count == 0:
            return BadRequestError(msg="Role not found")

        return SuccessResponse(msg="OK").send(data=True)
    except Exception as E:
        return InternalServerError(msg=str(E))
